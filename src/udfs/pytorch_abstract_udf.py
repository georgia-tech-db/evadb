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

from abc import ABC, abstractmethod
from typing import Any, List

import numpy as np
import torch
from torch import nn, Tensor
from torchvision.transforms import Compose, transforms

from src.models.inference.outcome import Outcome
from src.udfs.abstract_udfs import AbstractClassifierUDF
from src.udfs.gpu_compatible import GPUCompatible


class PytorchAbstractUDF(AbstractClassifierUDF, nn.Module, GPUCompatible, ABC):
    """
    A pytorch based classifier. Used to make sure we make maximum
    utilization of features provided by pytorch without reinventing the wheel.
    """

    def __init__(self):
        AbstractClassifierUDF.__init__(self)
        nn.Module.__init__(self)

    def get_device(self):
        return next(self.parameters()).device

    @property
    def transforms(self) -> Compose:
        return Compose([transforms.ToTensor()])

    def transform(self, images: Any):
        return self.transforms(images).to(self.get_device())

    def forward(self, frames: np.ndarray):
        return self.classify([self.transform(frame[0]) for frame in frames])

    @abstractmethod
    def classify(self, frames: Tensor) -> List[Outcome]:
        """
        Abstract method to work with tensors.
        Specified transformations are already applied
        Arguments:
            frames (Tensor): tensor on which transformation is performed
        Returns:
            List[Outcome]: outcome after prediction
        """

    def as_numpy(self, val: Tensor) -> np.ndarray:
        """
        Given a tensor in GPU, detach and get the numpy output
        Arguments:
             val (Tensor): tensor to be converted
        Returns:
            np.ndarray: numpy array representation
        """
        return val.detach().cpu().numpy()

    def to_device(self, device: str):
        """

        :param device:
        :return:
        """
        return self.to(torch.device("cuda:{}".format(device)))

    def __call__(self, *args, **kwargs):
        return nn.Module.__call__(self, *args, **kwargs)
