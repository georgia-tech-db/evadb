# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from eva.executor.abstract_executor import AbstractExecutor
from eva.plan_nodes.tune_plan import TunePlan
from eva.models.storage.batch import Batch
import math
import pandas as pd
import numpy as np
import zipfile
import os
import random
import shutil
from copy import deepcopy
from datetime import datetime

import torch
from torch.optim import lr_scheduler
import torch.nn as nn

from yolov5.models.yolo import Model
from yolov5.utils.dataloaders import create_dataloader
from yolov5.utils.loss import ComputeLoss
from yolov5.utils.general import intersect_dicts, check_img_size, colorstr, labels_to_class_weights, check_amp, check_git_info
from yolov5.utils.torch_utils import smart_optimizer, de_parallel, EarlyStopping, ModelEMA
import yolov5.val as validate
from yolov5.utils.metrics import fitness
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.services.table_catalog_service import TableCatalogService
from eva.catalog.services.column_catalog_service import ColumnCatalogService
from eva.utils.logging_manager import logger
from eva.executor.executor_utils import ExecutorError
from eva.storage.sqlite_storage_engine import SQLStorageEngine

def train_yolov5(batch_size, epochs, freeze_layers, multi_scale, train_path, val_path, nc):
    device = torch.device("cpu")
    start_epoch = 0
    best_fitness = 0.0
    last_opt_step = -1
    GIT_INFO = check_git_info()

    hyp = {
        'lr0': 0.01,'lrf': 0.01,'momentum': 0.937,'weight_decay': 0.0005,'warmup_epochs': 3.0,
        'warmup_momentum': 0.8,'warmup_bias_lr': 0.1,'box': 0.05,'cls': 0.5,'cls_pw': 1.0,
        'obj': 1.0,'obj_pw': 1.0,'iou_t': 0.2,'anchor_t': 4.0,'fl_gamma': 0.0,'hsv_h': 0.015,
        'hsv_s': 0.7,'hsv_v': 0.4,'degrees': 0.0,'translate': 0.1,'scale': 0.5,'shear': 0.0,
        'perspective': 0.0,'flipud': 0.0,'fliplr': 0.5,'mosaic': 1.0,'mixup': 0.0,'copy_paste': 0.0
    }

    # train_path = os.path.join(dataset_path, "images", "train")
    # val_path = os.path.join(dataset_path, "images", "valid")
    # nc = 7
    dataset_path = os.path.dirname(os.path.dirname(train_path))
    obj_names_file = os.path.join(dataset_path, "obj.names")

    with open(obj_names_file, 'r') as f:
        names = {i: name.strip() for i, name in enumerate(f)}

    last = os.path.join(dataset_path, "last.pt")
    best = os.path.join(dataset_path, "best.pt")
    save_weights = os.path.split(dataset_path)[-1] + '.pt'
    save_weights = os.path.join("data", "yolov5_weights", save_weights)


    # ckpt = torch.hub.load('ultralytics/yolov5', 'yolov5x', device='cpu')
    # cfg = 'yolov5/models/yolov5s.yaml'
    ckpt = torch.load('yolov5s.pt', map_location='cpu')
    model = Model(ckpt['model'].yaml, ch=3, nc=nc, anchors=hyp.get('anchors')).to(device)
    exclude = ['anchor'] if (hyp.get('anchors')) else []
    csd = ckpt['model'].float().state_dict()
    csd = intersect_dicts(csd, model.state_dict(), exclude=exclude)
    model.load_state_dict(csd, strict=False)
    amp = check_amp(model)

    gs = max(int(model.stride.max()), 32)
    imgsz = check_img_size(640, gs, floor=gs * 2)

    #freeze layer
    if freeze_layers != 0:
        freeze = [f'model.{x}.' for x in range(freeze_layers)]
        for k, v in model.named_parameters():
            v.requires_grad = True
            if any(x in k for x in freeze):
                v.requires_grad = False

    nbs = 64
    accumulate = max(round(nbs / batch_size), 1)
    hyp['weight_decay'] *= batch_size * accumulate / nbs
    optimizer = smart_optimizer(model, "Adam", hyp['lr0'], hyp['momentum'], hyp['weight_decay'])  

    lf = lambda x: (1 - x / epochs) * (1.0 - hyp['lrf']) + hyp['lrf']
    scheduler = lr_scheduler.LambdaLR(optimizer, lr_lambda=lf)
    ema = ModelEMA(model)


    train_loader, dataset = create_dataloader(train_path,imgsz,batch_size,gs,
                                              single_cls=False,hyp=hyp,
                                              augment=True,cache=None,
                                              rect=True,rank=-1,workers=4,
                                              image_weights=False,quad=False,
                                              prefix=colorstr('train: '),
                                              shuffle=True)

    
    labels = np.concatenate(dataset.labels, 0)
    mlc = int(labels[:, 0].max())

    val_loader = create_dataloader(val_path,imgsz,batch_size,gs,
                                   single_cls=False,hyp=hyp,
                                   cache=None,rect=True,rank=-1,
                                   workers=4,pad=0.5,
                                   prefix=colorstr('val: '))[0]
    
    model.half().float()

    nl = de_parallel(model).model[-1].nl
    hyp['box'] *= 3 / nl
    hyp['cls'] *= nc / 80 * 3 / nl
    hyp['obj'] *= (imgsz / 640) ** 2 * 3 / nl
    hyp['label_smoothing'] = 0.1
    model.nc = nc
    model.hyp = hyp
    model.class_weights = labels_to_class_weights(dataset.labels, nc).to(device) * nc
    model.names = names

    # training
    nb = len(train_loader)
    warmup_epochs = 3
    nw = max(round(warmup_epochs * nb), 100)
    nw = min(nw, (epochs - start_epoch) / 2 * nb)
    last_opt_step = -1
    maps = np.zeros(nc)
    results = (0, 0, 0, 0, 0, 0, 0)
    scheduler.last_epoch = start_epoch - 1
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    stopper, stop = EarlyStopping(patience=10), False
    compute_loss = ComputeLoss(model)

    training_results = {
        "epochs": [],
        "Precision": [],
        "Recall": [],
        "mAP50": [],
        "mAP50-95": [],
        "obj_loss": []
    }

    for epoch in range(start_epoch, epochs):
        model.train()
        mloss = torch.zeros(3, device=device)
        # train_loader.sampler.set_epoch(epoch)
        optimizer.zero_grad()
        for i, (imgs, targets, paths, _) in enumerate(train_loader):
            ni = i + nb * epoch
            imgs = imgs.to(device, non_blocking=True).float()/255
            # warmup
            if ni <= nw:
                xi = [0, nw]
                accumulate = max(1, np.interp(ni, xi, [1, nbs / batch_size]).round())
                for j, x in enumerate(optimizer.param_groups):
                    x['lr'] = np.interp(ni, xi, [hyp['warmup_bias_lr'] if j == 0 else 0.0, x['initial_lr'] * lf(epoch)])
                    if 'momentum' in x:
                        x['momentum'] = np.interp(ni, xi, [hyp['warmup_momentum'], hyp['momentum']])
            # multi scale
            if multi_scale:
                sz = random.randrange(int(imgsz * 0.5), int(imgsz * 1.5) + gs) // gs * gs
                sf = sz / max(imgs.shape[2:])
                if sf != 1:
                    ns = [math.ceil(x * sf / gs) * gs for x in imgs.shape[2:]]
                    imgs = nn.functional.interpolate(imgs, size=ns, mode='bilinear', align_corners=False)
            # forward
            pred = model(imgs)
            loss, loss_items = compute_loss(pred, targets.to(device))
            # backward
            scaler.scale(loss).backward()
            # optimize
            if ni - last_opt_step >= accumulate:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
                if ema:
                    ema.update(model)
                last_opt_step = ni

        lr = [x['lr'] for x in optimizer.param_groups]
        scheduler.step()

        ema.update_attr(model, include=['yaml', 'nc', 'hyp', 'names', 'stride', 'class_weights'])
        final_epoch = (epoch + 1 == epochs) or stopper.possible_stop
        data_paths = {'train': train_path, 'val': val_path, 'nc': nc}
        save_dir = dataset_path
        if not final_epoch:
            results, maps, _ = validate.run(data_paths, batch_size=batch_size,
                                            imgsz=imgsz, half=amp, model=ema.ema,
                                            single_cls=False, dataloader=val_loader,
                                            save_dir=save_dir, plots=False,
                                            compute_loss=compute_loss)
        fi = fitness(np.array(results).reshape(1, -1))
        stop = stopper(epoch=epoch, fitness=fi)
        if fi > best_fitness:
            best_fitness = fi
        log_vals = list(mloss) + list(results) + lr

        training_results["epochs"].append(epoch)
        training_results["Precision"].append(log_vals[3])       
        training_results["Recall"].append(log_vals[4])
        training_results["mAP50"].append(log_vals[5])
        training_results["mAP50-95"].append(log_vals[6])
        training_results['obj_loss'].append(log_vals[7])

        if final_epoch:
            ckpt = {
                'epoch': epoch,
                'best_fitness': best_fitness,
                'model': deepcopy(de_parallel(model)).half(),
                'ema': deepcopy(ema.ema).half(),
                'updates': ema.updates,
                'optimizer': optimizer.state_dict(),
                'git': GIT_INFO,
                'date': datetime.now().isoformat()}

            # Save last, best for future use and delete
            torch.save(ckpt, last)
            if best_fitness == fi:
                torch.save(ckpt, best)
                torch.save(ckpt, save_weights)
            del ckpt

        if stop:
            break

    return training_results

class TuneExecutor(AbstractExecutor):
    def __init__(self, node: TunePlan):
        super().__init__(node)
        self.catalog = CatalogManager()
        self.table = TableCatalogService()
        self.batch = SQLStorageEngine()

    def exec(self, *args, **kwargs):
        table = self.node.table_info
        table_info = table[0]

        table_name = table_info.table_name
        database_name = table_info.database_name
        batch_size = int(self.node.batch_size)
        epochs_size = int(self.node.epochs_size)
        freeze_layer = int(self.node.freeze_layer)
        multi_scale = self.node.multi_scale
        show_train_progress = self.node.show_train_progress

        check_table = self.catalog.check_table_exists(table_name, database_name)

        if check_table == False:
            error = f"{table_name} does not exist."
            logger.error(error)
            raise ExecutorError(error)
        else:
            table_obj = self.table.get_entry_by_name(database_name, table_name)
            table_col = self.batch.read(table_obj)

            for df in table_col:
                for _, row in df.iterrows():
                    train_path = row['train_path']
                    val_path = row['val_path']
                    num_classes = row['num_classes']
        
        training_results = train_yolov5(batch_size, epochs_size, freeze_layer, multi_scale, train_path, val_path, num_classes)

        yield Batch(pd.DataFrame(training_results))

        if show_train_progress:
            yield Batch(pd.DataFrame(training_results))
        else:
            yield Batch(pd.DataFrame(training_results).iloc[-1])
