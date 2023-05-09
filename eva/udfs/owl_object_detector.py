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
import logging
from typing import List
import numpy as np
import pandas as pd

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.abstract.abstract_udf import AbstractUDF
from transformers import OwlViTProcessor, OwlViTForObjectDetection
from eva.utils.logging_manager import logger
from eva.udfs.gpu_compatible import GPUCompatible
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe

try:
    import torch
    from torch import Tensor

except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install torch`"
    )


class OwlObjectDetector(AbstractUDF, GPUCompatible):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "yolo"

    def to_device(self, device: str):
        self.device = device
        return self

    @setup(cachable=True, udf_type="object_detection", batchable=True)
    def setup(self, threshold=0.3):
        logging.getLogger("hf_oneshot").setLevel(logging.CRITICAL)  # yolov5
        self.threshold = threshold
        self.processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
        self.model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")
        # self.model = torch.hub.load("ultralytics/yolov5", "yolov5s", verbose=False)
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
        # Stacking all frames, and changing to numpy
        # because of yolov5 error with Tensors
        print("Does this work?")
        outcome = []
        # Convert to HWC
        # https://github.com/ultralytics/yolov5/blob/3e55763d45f9c5f8217e4dad5ba1e6c1f42e3bf8/models/common.py#L658
        frames = np.ravel(frames.to_numpy())
        frames = torch.permute(frames, (0, 2, 3, 1))
        logger.warn("Does this work?1")
        logger.warn("Does this work?2")    
        inputs = self.processor(text=[self.labels], images=frames, return_tensors="pt")
        logger.warn("Does this work?3")
        outputs = self.model(**inputs)
        logger.warn("Does this work?4")
        results = self.processor.post_process(outputs=outputs)
        logger.warn(outputs)
        logger.warn(results)
        for i in range(frames.shape[0]):
            
            single_result = results.pandas().xyxy[i]
            pred_class = single_result["labels"].tolist()
            pred_score = single_result["scores"].tolist()
            pred_boxes = single_result["boxes"].apply(
                lambda x: list(x), axis=1
            )

            outcome.append(
                {
                    "labels": pred_class,
                    "bboxes": pred_boxes,
                    "scores": pred_score,
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