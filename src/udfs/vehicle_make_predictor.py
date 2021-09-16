# coding=utf-8
# Copyright 2018-2020 EVA
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


import os
from typing import List

import numpy as np
import pandas as pd
import scipy.io as sio 
import torchvision

import torch
import torchvision
from torch import Tensor
from torch import nn
from torchvision.transforms import Compose, transforms

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.pytorch_abstract_udf import PytorchAbstractUDF
from src.configuration.dictionary import EVA_DIR
from src.udfs.fastrcnn_object_detector import FastRCNNObjectDetector


class CarRecognitionModel(nn.Module):
    def __init__(self):
        super(CarRecognitionModel, self).__init__()

        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        resnet = torchvision.models.resnet50(pretrained=True)

        # Remove linear layer
        modules = list(resnet.children())[:-1]
        self.resnet = nn.Sequential(*modules)
        self.resnet.to(self.device)
        # self.pool = nn.AvgPool2d(kernel_size=7)
        num_classes = 196
        self.fc = nn.Linear(2048, num_classes)
        self.softmax = nn.Softmax(dim=1)
        self.transforms = Compose([
            transforms.ToPILImage(),
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def forward(self, images):
        x = self.transforms(torch.squeeze(images))
        x = self.resnet(x.unsqueeze(0).to(self.device))  # [N, 2048, 1, 1]
        # x = self.pool(x)
        x = x.view(-1, 2048)  # [N, 2048]
        x = self.fc(x)
        x = self.softmax(x)
        return x


class VehicleMakePredictor(PytorchAbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "vehicle_make"

    def __init__(self, threshold=0.85):
        super().__init__()

        # loading fasterrcnn model
        self.threshold = threshold
        self.fastrcnn_model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        self.fastrcnn_model.eval()

        # loading the custom car make model
        custom_model_path = os.path.join(EVA_DIR, "data", "models", "vehicle_make_predictor", "car_recognition.pt")
        self.car_make_model = CarRecognitionModel()
        self.car_make_model.load_state_dict(torch.load(custom_model_path))
        self.car_make_model.eval()

        # loading label names for the car makes
        car_meta_path = os.path.join(EVA_DIR, "data", "models", "vehicle_make_predictor", "cars_meta.mat")
        cars_meta = sio.loadmat(car_meta_path)
        self.class_names = cars_meta['class_names']
        self.class_names = np.transpose(self.class_names)

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
            '__background__', 'person', 'bicycle', 'car', 'motorcycle',
            'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A',
            'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
            'cow',
            'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack',
            'umbrella', 'N/A', 'N/A',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
            'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard',
            'surfboard', 'tennis racket',
            'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
            'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza',
            'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A',
            'dining table',
            'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote',
            'keyboard', 'cell phone',
            'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A',
            'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        """
        Performs predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need
            to be performed

        Returns:
            tuple containing predicted_classes (List[List[str]]),
            predicted_boxes (List[List[BoundingBox]]),
            predicted_scores (List[List[float]])

        """

        predictions = self.fastrcnn_model(frames)       
        outcome = pd.DataFrame()
        for prediction in predictions:
            pred_class = [str(self.labels[i]) for i in
                          list(self.as_numpy(prediction['labels']))]
            pred_boxes = [[[i[0], i[1]],
                           [i[2], i[3]]]
                          for i in
                          list(self.as_numpy(prediction['boxes']))]
            pred_score = list(self.as_numpy(prediction['scores']))
            preds_t = [pred_score.index(x) for x in pred_score if x > self.threshold]

            # check if there is atleast 1 prediction above our threshold, if not continue
            if len(preds_t) > 0: 
                pred_t = preds_t[-1]
            else:
                continue

            pred_boxes = np.array(pred_boxes[:pred_t + 1])
            pred_class = np.array(pred_class[:pred_t + 1])
            pred_score = np.array(pred_score[:pred_t + 1])
            
            num_preds = len(pred_boxes)

            # using a new list specifically for cars
            car_pred_boxes = []
            car_pred_class = []
            car_pred_score = []
            car_make_preds = []
            for i in range(num_preds):

                # this model will run only on cars
                if pred_class[i] != 'car':
                    continue 

                x1, y1, x2, y2 = int(pred_boxes[i][0][0]), int(pred_boxes[i][0][1]), int(pred_boxes[i][1][0]), int(pred_boxes[i][1][1])
                
                # cropping this frame to get the individual car
                cropped_frame = frames[:, :, y1:y2, x1:x2]

                # invoke our custom car make model
                preds = self.car_make_model(cropped_frame)
                label_index = int(preds.max(1)[1][0])
                
                car_pred_boxes.append(pred_boxes[i])
                car_pred_class.append(pred_class[i])
                car_pred_score.append(pred_score[i])
                car_make_preds.append(self.class_names[label_index])

            outcome = outcome.append(
                {
                    "labels": np.array(car_pred_class),
                    "scores": np.array(car_pred_score),
                    "boxes": np.array(car_pred_boxes),
                    "makes": np.array(car_make_preds)
                },
                ignore_index=True)
            


        return outcome
