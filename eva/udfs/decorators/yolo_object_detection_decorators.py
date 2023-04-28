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
from typing import List

import pandas as pd

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.abstract.pytorch_abstract_udf import PytorchAbstractClassifierUDF
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe, PyTorchTensor

try:
    import torch
    from torch import Tensor
    from ultralytics import YOLO

except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install torch`"
    )


class Yolo(PytorchAbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "yolo"

    @setup(cachable=True, udf_type="object_detection", batchable=True)
    def setup(self, threshold=0.85):
        self.threshold = threshold
        self.predict_func = YOLO("yolov8m.pt")
        self.model = self.predict_func.model

    @property
    def labels(self) -> List[str]:
        return [
            "__background__",
            "person",
            "bicycle",
            "car",
            "motorcycle",
            "airplane",
            "bus",
            "train",
            "truck",
            "boat",
            "traffic light",
            "fire hydrant",
            "N/A",
            "stop sign",
            "parking meter",
            "bench",
            "bird",
            "cat",
            "dog",
            "horse",
            "sheep",
            "cow",
            "elephant",
            "bear",
            "zebra",
            "giraffe",
            "N/A",
            "backpack",
            "umbrella",
            "N/A",
            "N/A",
            "handbag",
            "tie",
            "suitcase",
            "frisbee",
            "skis",
            "snowboard",
            "sports ball",
            "kite",
            "baseball bat",
            "baseball glove",
            "skateboard",
            "surfboard",
            "tennis racket",
            "bottle",
            "N/A",
            "wine glass",
            "cup",
            "fork",
            "knife",
            "spoon",
            "bowl",
            "banana",
            "apple",
            "sandwich",
            "orange",
            "broccoli",
            "carrot",
            "hot dog",
            "pizza",
            "donut",
            "cake",
            "chair",
            "couch",
            "potted plant",
            "bed",
            "N/A",
            "dining table",
            "N/A",
            "N/A",
            "toilet",
            "N/A",
            "tv",
            "laptop",
            "mouse",
            "remote",
            "keyboard",
            "cell phone",
            "microwave",
            "oven",
            "toaster",
            "sink",
            "refrigerator",
            "N/A",
            "book",
            "clock",
            "vase",
            "scissors",
            "teddy bear",
            "hair drier",
            "toothbrush",
        ]

    @forward(
        input_signatures=[
            PyTorchTensor(
                name="input_col",
                is_nullable=False,
                type=NdArrayType.FLOAT32,
                dimensions=(1, 3, 540, 960),
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
    def forward(self, frames: Tensor) -> pd.DataFrame:
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
        # Stacking all frames, and changing to numpy
        # because of Yolo error with Tensors

        outcome = []
        # Convert to HWC
        frames = torch.permute(frames, (0, 2, 3, 1))
        list_of_numpy_images = [its.cpu().detach().numpy() * 255 for its in frames]
        predictions = self.predict_func(list_of_numpy_images)

        for pred in predictions:
            single_result = pred.boxes
            pred_class = [
                self.predict_func.names[i] for i in single_result.cls.tolist()
            ]
            pred_score = single_result.conf.tolist()
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
