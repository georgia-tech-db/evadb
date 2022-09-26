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
from abc import ABCMeta

import pandas as pd
import numpy as np
from numpy.typing import ArrayLike

from eva.udfs.udf import UDF
from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd
import torch
from numpy.typing import ArrayLike
from PIL import Image
from torch import Tensor, nn

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace


try:
    from torch import Tensor
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install torch`"
    )

try:
    import torchvision
except ImportError as e:
    raise ImportError(
        f"Failed to import with error {e}, \
        please try `pip install torch`"
    )

"""
    `setup` is the name of the decorator.
"""
def setup(
    name=None,
    cache=True
    ):
    def Inner(func):
        def wrapper(self):
            return func(self)
        return wrapper
    return Inner

def preprocess():
    def Inner(func):
        def wrapper(self):
            return func(self)
        return wrapper
    return Inner

def forward():
    def Inner(func):
        def wrapper(self, frames):
            return func(self, frames)
        return wrapper
    return Inner


class FastRCNNObjectDetectorUDF(UDF):
    def __init__(self):
        UDF.__init__(self)
        self.setup()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @setup(
        name="FastRCNNObjectDetectorUDF",
        cache=True
    )
    def setup(self, threshold=0.85):
        # ctx points to the class
        self.threshold = threshold
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            pretrained=True, progress=False
        )
        self.model.eval()


    @preprocess()
    def preprocess(self):
        pass

    @forward()
    def forward(self, frames: Tensor):
        tens_batch = torch.cat([self.transform(x) for x in frames]).to(self.get_device())
        return self.classify(tens_batch)

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


    def __call__(self, *args, **kwargs):
        print("Entered the call method")
        if len(args) == 0:
            return nn.Module.__call__(self, *args, **kwargs)

        frames = args[0]
        if isinstance(frames, pd.DataFrame):
            frames = frames.transpose().values.tolist()[0]

        print("Abbout to enter the UDF Call Method")
        return nn.Module.__call__(self, frames, **kwargs)