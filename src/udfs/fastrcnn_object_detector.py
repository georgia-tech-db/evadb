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

from torch import Tensor
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.pytorch_abstract_udf import PytorchAbstractUDF


class FastRCNNObjectDetector(PytorchAbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "fastrcnn"

    def __init__(self, threshold=0.5):
        super().__init__()
        self.threshold = threshold
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            pretrained=True)
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
        predictions = self.model(frames)
        outcome = pd.DataFrame()
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
            pred_boxes = list(pred_boxes[:pred_t + 1])
            pred_class = list(pred_class[:pred_t + 1])
            pred_score = list(pred_score[:pred_t + 1])
            outcome = outcome.append(
                {
                    "label": pred_class[0],
                    "pred_score": pred_score[0],
                    "pred_boxes": pred_boxes[0]
                },
                ignore_index=True)
        return outcome
