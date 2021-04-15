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

import pandas as pd
from torch import nn
from PIL import Image
from torchvision import transforms

from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.filters.abstract_filter import AbstractFilter
from src.udfs.gpu_compatible import GPUCompatible


class PytorchAbstractFilter(AbstractFilter, nn.Module, GPUCompatible, ABC):
    """
    A PyTorch based filter.
    """

    def __init__(self):
        AbstractFilter.__init__(self)
        nn.Module.__init__(self)

    def get_device(self):
        return next(self.parameters()).device

    @property
    def transforms(self) -> Compose:
        return transforms.Compose([
            transforms.Lambda(lambda x: Image.fromarray(x[:, :, ::-1])),
            transforms.ToTensor(),
            transforms.Resize((224, 224)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), 
            transforms.Lambda(lambda x: x.unsqueeze(0))
        ])

    def transform(self, images: np.ndarray):
        return self.transforms(images)

    def forward(self, frames: List[np.ndarray]):
        tens_batch = torch.cat([self.transform(x) for x in frames])\
            .to(self.get_device())
        return self.classify(tens_batch)

    @abstractmethod 
    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        """
        Abstract method to work with tensors.
        Specified transformations are already applied.
        Arguments:
            frames (Tensor): tensor on which transformation is performed
        Returns:
            pd.DataFrame: outcome after prediction
        """

    def classify(self, frames: Tensor) -> pd.DataFrame:
        """
        Given the gpu_batch_size, we split the input tensor into chunks,
        and call the _get_predictions and merge the results.
        Arguments:
            frames (Tensor): tensor on which transformation is performed
        Returns:
            pd.DataFrame: outcome after prediction
        """
        gpu_batch_size = ConfigurationManager()\
            .get_value('executor', 'gpu_batch_size')

        if gpu_batch_size:
            chunks = torch.split(frames, gpu_batch_size)
            outcome = pd.DataFrame()
            for tensor in chunks:
                outcome = outcome.append(self._get_predictions(tensor),
                                         ignore_index=True)
            return outcome
        else:
            return self._get_predictions(frames)

    def as_numpy(self, val: Tensor) -> np.ndarray:
        """
        Given a tensor in GPU, detach and get the numpy output.
        Arguments:
             val (Tensor): tensor to be converted
        Returns:
            np.ndarray: numpy array representation
        """
        return val.detach().cpu().numpy()

    def to_device(self, device: str):
        """
        Transfer filter to specified device.
        Arguments:
            device (str): device's string identifier
        Returns:
            New instance on desired device
        """
        return self.to(torch.device("cuda:{}".format(device)))

    def __call__(self, *args, **kwargs):
        frames = None
        if len(args):
            frames = args[0]
        if isinstance(frames, pd.DataFrame):
            frames = frames.transpose().values.tolist()[0]
        return nn.Module.__call__(self, frames, **kwargs)
