# coding=utf-8
# Copyright 2018-2023 EvaDB
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

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.udfs.gpu_compatible import GPUCompatible
from evadb.utils.generic_utils import try_to_import_ultralytics


class Yolo(AbstractUDF, GPUCompatible):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score
    """

    @property
    def name(self) -> str:
        return "yolo"

    @setup(cacheable=True, udf_type="object_detection", batchable=True)
    def setup(self, model: str, threshold=0.3):
        try_to_import_ultralytics()
        from ultralytics import YOLO

        self.threshold = threshold
        self.model = YOLO(model)
        self.device = "cpu"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["labels", "bboxes", "scores"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                ],
                column_shapes=[(None,), (None,), (None,)],
            )
        ],
    )
    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
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
        outcome = []
        # Fix me: this should be taken care by decorators
        frames = np.ravel(frames.to_numpy())
        list_of_numpy_images = [its for its in frames]
        predictions = self.model.predict(
            list_of_numpy_images, device=self.device, conf=self.threshold, verbose=False
        )
        for pred in predictions:
            single_result = pred.boxes
            pred_class = [self.model.names[i] for i in single_result.cls.tolist()]
            pred_score = single_result.conf.tolist()
            pred_score = [round(conf, 2) for conf in single_result.conf.tolist()]
            pred_boxes = single_result.xyxy.tolist()
            sorted_list = list(map(lambda i: i < self.threshold, pred_score))
            t = sorted_list.index(True) if True in sorted_list else len(sorted_list)
            outcome.append(
                {
                    "labels": pred_class[:t],
                    "bboxes": pred_boxes[:t],
                    "scores": pred_score[:t],
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

    def to_device(self, device: str):
        self.device = device
        return self
