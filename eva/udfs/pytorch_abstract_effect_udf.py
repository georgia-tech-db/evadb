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
from typing import List

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch import nn, Tensor
from torchvision.transforms import Compose, transforms

from eva.udfs.abstract_udfs import AbstractClassifierUDF
from eva.udfs.gpu_compatible import GPUCompatible
from eva.configuration.configuration_manager import ConfigurationManager


class PytorchAbstractEffectUDF(AbstractEffectUDF, nn.Module, GPUCompatible, ABC):
    """
    A pytorch based classifier. Used to make sure we make maximum
    utilization of features provided by pytorch without reinventing the wheel.
    """

    def __init__(self):
        AbstractEffectUDF.__init__(self)
        nn.Module.__init__(self)

    def get_device(self):
        return next(self.parameters()).device

    @property
    def transforms(self) -> Compose:
        return Compose([transforms.ToTensor()])

    def transform(self, images: np.ndarray):
        # reverse the channels from opencv
        return self.transforms(Image.fromarray(images[:, :, ::-1]))\
            .unsqueeze(0)

    def forward(self, frames: List[np.ndarray]):
        tens_batch = torch.cat([self.transform(x) for x in frames])\
            .to(self.get_device())
        return self.classify(tens_batch)

    @abstractmethod
    def _get_frames(self, frames: Tensor) -> Tensor:
        """
        Abstract method to work with tensors.
        Specified transformations are already applied
        Arguments:
            frames (Tensor): tensor on which transformation is performed
        Returns:
            Tensor: frames after filter has been applied
        """

    def apply(self, frames: Tensor) -> List[Tensor]:
        """
        Given the gpu_batch_size, we split the input tensor inpto chunks.
        And call the _get_predictions and merge the results.
        Arguments:
            frames (Tensor): tensor on which transformation is performed
        Returns:
            Tensor: frames after filter has been applied
        """
        gpu_batch_size = ConfigurationManager()\
            .get_value('executor', 'gpu_batch_size')

        if gpu_batch_size:
            chunks = torch.split(frames, gpu_batch_size)
            outcome = []
            for tensor in chunks:
                outcome = outcome.append(self._get_frames(tensor))

            return outcome
        else:
            return self._get_frames(frames)

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
        Sends computation to a GPU.
        Arguments:
            device: name or ID associated to GPU
        Returns:
            self: new instance of UDF on GPU
        """
        return self.to(torch.device("cuda:{}".format(device)))

    def __call__(self, *args, **kwargs):
        frames = None
        if len(args):
            frames = args[0]
        if isinstance(frames, pd.DataFrame):
            frames = frames.transpose().values.tolist()[0]
        return nn.Module.__call__(self, frames, **kwargs)
