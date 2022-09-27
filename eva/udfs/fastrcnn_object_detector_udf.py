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

from eva.udfs.udf import UDF
from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd
import torch
from numpy.typing import ArrayLike
from PIL import Image
from torch import Tensor, nn
from torchvision.transforms import Compose, transforms

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.udfs.gpu_compatible import GPUCompatible
from eva.configuration.configuration_manager import ConfigurationManager

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

def setup(name=None,cache=True):
    def Inner(func):
        def wrapper(self):
            # self.name = name
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

class FastRCNNObjectDetectorUDF(nn.Module, GPUCompatible):
    def __init__(self):
        nn.Module.__init__(self)
        self.transforms = [transforms.ToTensor()]
        self.setup()

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)
    
    @property
    def name(self) -> str:
        return str(self)

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
    
    def classify(self, frames: Tensor) -> pd.DataFrame:
        gpu_batch_size = ConfigurationManager().get_value("executor", "gpu_batch_size")
        if gpu_batch_size:
            chunks = torch.split(frames, gpu_batch_size)
            outcome = pd.DataFrame()
            for tensor in chunks:
                outcome = outcome.append(
                    self._get_predictions(tensor), ignore_index=True
                )
            return outcome
        else:
            return self._get_predictions(frames)

    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        predictions = self.model(frames)
        outcome = pd.DataFrame()
        for prediction in predictions:
            pred_class = [
                str(self.labels[i]) for i in list(self.as_numpy(prediction["labels"]))
            ]
            pred_boxes = [
                [i[0], i[1], i[2], i[3]]
                for i in list(self.as_numpy(prediction["boxes"]))
            ]
            pred_score = list(self.as_numpy(prediction["scores"]))
            valid_pred = [pred_score.index(x) for x in pred_score if x > self.threshold]

            if valid_pred:
                pred_t = valid_pred[-1]
            else:
                pred_t = -1

            pred_boxes = np.array(pred_boxes[: pred_t + 1])
            pred_class = np.array(pred_class[: pred_t + 1])
            pred_score = np.array(pred_score[: pred_t + 1])
            outcome = outcome.append(
                {"labels": pred_class, "scores": pred_score, "bboxes": pred_boxes},
                ignore_index=True,
            )
        return outcome

    def as_numpy(self, val: Tensor) -> np.ndarray:
        """
        Given a tensor in GPU, detach and get the numpy output
        Arguments:
             val (Tensor): tensor to be converted
        Returns:
            np.ndarray: numpy array representation
        """
        return val.detach().cpu().numpy()

    def to_device(self, device: str) -> GPUCompatible:
        """
        Required to make class a member of GPUCompatible Protocol.
        """
        return self.to(torch.device("cuda:{}".format(device)))

    
    def get_device(self):
        return next(self.parameters()).device
    
    def transform(self, images: np.ndarray):
        composed = Compose(self.transforms)
        # reverse the channels from opencv
        return composed(Image.fromarray(images[:, :, ::-1])).unsqueeze(0)

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
        if len(args) == 0:
            return nn.Module.__call__(self, *args, **kwargs)

        frames = args[0]
        if isinstance(frames, pd.DataFrame):
            frames = frames.transpose().values.tolist()[0]

        return nn.Module.__call__(self, frames, **kwargs)