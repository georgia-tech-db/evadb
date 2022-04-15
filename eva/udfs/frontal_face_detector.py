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
from typing import List

import pandas as pd
import torchvision
import numpy as np

import torch

from torch import Tensor
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.pytorch_abstract_udf import PytorchAbstractUDF

import torchvision.transforms as T

#import cv2
from facenet_pytorch import MTCNN
#import argparse
import dlib
#import PIL


class FrontalFaceDetector(PytorchAbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "frontalface"

    def __init__(self, threshold=0.85):
        super().__init__()
        self.threshold = threshold
        self.model = MTCNN(post_process=True)
        self.model.eval()

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

    def rect_to_bb(self, rect):
        x = rect.left()
        y = rect.top()
        w = rect.right() - x 
        h = rect.bottom() - y 
        return (x, y, w, h)

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
        detector = dlib.get_frontal_face_detector()

        copy = torch.squeeze(frames)
        transform = T.ToPILImage()
        copy2 = transform(copy)
        copy3 = np.array(copy2)
        face = detector(copy3, 1)
        x = 0
        y = 0
        w = 0
        h = 0
        pred_boxes = []
        for (i, rect) in enumerate(face):
            x = rect.left()
            y = rect.top()
            w = rect.right()
            h = rect.bottom()
            pred_boxes.append(rect)
        
        score = 1
        labeling = "face"
        outcome = pd.DataFrame()

        if(x == 0 and y == 0 and w == 0 and h == 0):
            labeling = "undetected"
            score = 0
            pred_boxes = [[0,0], [0,0],[0,0], [0,0]]

        pred_boxes = [[x,y], [w,y],[x,h], [w,h]]

        outcome = outcome.append(
            {
                "labels": labeling,
                "scores": score,
                "boxes": pred_boxes
            },
            ignore_index=True)
        #outcome = outcome.reset_index(drop=True)
        #print(outcome)
        return outcome
