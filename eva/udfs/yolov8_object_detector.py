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
import numpy as np
import pandas as pd

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe
from eva.utils.logging_manager import logger


from ultralytics import YOLO

class Yolov8(AbstractUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "yolo"
        
    def setup(self, threshold=0.3):
        self.threshold = threshold
        self.model = YOLO("yolov8s.pt")
        self.device = "cpu"

    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
        
        labels1 =['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 
                  'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 
                  'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 
                  'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 
                  'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 
                  'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 
                  'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 
                  'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 
                  'teddy bear', 'hair drier', 'toothbrush']


        outcome = []

        frames = np.ravel(frames.to_numpy())
        images = [its for its in frames]
        predictions = self.model.predict(
            images, conf=self.threshold, verbose=False
        )

        for pred in predictions:
            single_result = pred.boxes
            # logger.warn(self.model.names)
            classes = [labels1[int(i)] for i in single_result.cls.tolist()]
            scores = [round(conf, 2) for conf in single_result.conf.tolist()]
            boxes = single_result.xyxy.tolist()

            sorted_list = list(map(lambda i: i < self.threshold, scores))
            res = sorted_list.index(True) if True in sorted_list else len(sorted_list)

            outcome.append(
                {
                    "labels": classes[:res],
                    "bboxes": boxes[:res],
                    "scores": scores[:res],
                },
            )
        return pd.DataFrame(
            outcome,
            columns=[
                "labels",
                "bboxes",
                "scores",
            ],
        )