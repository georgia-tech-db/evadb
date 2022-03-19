import ray
import cv2
import torchvision
import torch
import pandas as pd
import numpy as np
import time

from ray.util.queue import Queue
from torchvision.transforms import Compose, transforms
from PIL import Image

ray.init()

@ray.remote
class RayStageSink:

    def __init__(self, funcs):
        self.funcs = []
        for f in funcs:
            if hasattr(f, 'prepare'):
                f.prepare()
            self.funcs.append(f)

    def run(self, input_queue):
        if len(input_queue) > 1:
            raise NotImplemented

        self.execution_count = 0
        while True:
            next_item = input_queue[0].get(block=True)
            if next_item is None:
                input_queue[0].put(None)
                break
            for f in self.funcs:
                next_item = f(next_item)
            self.execution_count += 1

    def get_execution_count(self):
        return self.execution_count


def read(batch_size=1):
    video = cv2.VideoCapture('5-detrac.mp4')

    batch = []
    _, frame = video.read()
    #count = 0
    while frame is not None:
        batch.append(frame)
        #count += 1
        #if count > 100:
        #    break
        if len(batch) >= batch_size:
            yield batch
            batch =[]
        _, frame = video.read()
    if len(batch) > 0:
        yield batch

class FastRCNN:

    def __init__(self):
        pass

    def prepare(self):
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        self.model.eval()
        self.device = torch.device('cuda')
        _ = self.model.to(self.device)
        self.threshold = 0.85

    @property
    def labels(self):
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

    def as_numpy(self, val):
        """
        Given a tensor in GPU, detach and get the numpy output
        Arguments:
             val (Tensor): tensor to be converted
        Returns:
            np.ndarray: numpy array representation
        """
        return val.detach().cpu().numpy()

    def run(self, queue):
        self.row = 0
        while True:
            next_item = queue.get(block=True)
            if next_item is None:
                queue.put(None)
                break
            _ = self.__call__(next_item)
            self.row += len(next_item)
            if self.row % 100 == 0:
                print('Completed row: %s' % self.row)

    def get_total_rows(self):
        return self.row

    def __call__(self, frames):
        c = Compose([transforms.ToTensor()])
        tensor = torch.cat([c(Image.fromarray(x[:, :, ::-1])).unsqueeze(0) for x in frames]).to(self.device)
        predictions = self.model(tensor)
        outcome = []
        for prediction in predictions:
            pred_class = [str(self.labels[i]) for i in
                          list(self.as_numpy(prediction['labels']))]
            pred_boxes = [[[i[0], i[1]],
                           [i[2], i[3]]]
                          for i in
                          list(self.as_numpy(prediction['boxes']))]
            pred_score = list(self.as_numpy(prediction['scores']))
            pred_t = \
                [pred_score.index(x) for x in pred_score if
                 x > self.threshold][-1]
            pred_boxes = np.array(pred_boxes[:pred_t + 1])
            pred_class = np.array(pred_class[:pred_t + 1])
            pred_score = np.array(pred_score[:pred_t + 1])
            outcome.append(pred_class)
        return outcome

s = time.perf_counter()
it = read(20)
count = 0
"""
for frame in it:
    res = f(frame)
    count += 1
    if count % 100 == 0:
        print('Completed rows: %s' % count)
print("Total row: %s" % count)
e = time.perf_counter()

print('Total cost: %.2f' % (e-s))

window = []
for frame in it:
    window.append(frame)
    if len(window) >= 4:
        pipe = ray.data.from_items(window).window(blocks_per_window=1)
        pipe = pipe.map(FastRCNN, compute="actors", num_gpus=1)
        for res in pipe.iter_rows():
            count += 1
        window = []
if len(window) >= 4:
    pipe = ray.data.from_items(window).window(blocks_per_window=1)
    pipe = pipe.map(FastRCNN, compute="actors", num_gpus=1)
    for res in pipe.iter_rows():
        count += 1
print("Total row: %s" % count)
e = time.perf_counter()
print('Total cost: %.2f' % (e-s))
"""

queue = Queue(maxsize=100)

consumers = []
for _ in range(2):
    fast = FastRCNN()
    consumers.append(RayStageSink.options(num_gpus=1).remote([fast]))

tasks = []
for c in consumers:
    tasks.append(c.run.remote([queue]))


for batch in it:
    queue.put(batch)
queue.put(None)

ray.wait(tasks)
e = time.perf_counter()
for c in consumers:
    print('Total execution: %s' % ray.get(c.get_execution_count.remote()))
print('Total cost: %.2f' % (e-s))
