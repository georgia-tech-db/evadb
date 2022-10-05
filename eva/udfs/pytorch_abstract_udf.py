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

import numpy as np
import pandas as pd
import torch
from numpy.typing import ArrayLike
from PIL import Image
from torch import Tensor, nn
from torchvision.transforms import Compose, transforms

from eva.configuration.configuration_manager import ConfigurationManager
from eva.udfs.abstract_udf import AbstractClassifierUDF, AbstractTransformationUDF, InputType
from eva.udfs.gpu_compatible import GPUCompatible


class PytorchAbstractClassifierUDF(AbstractClassifierUDF, nn.Module, GPUCompatible):
    """
    A pytorch based classifier. Used to make sure we make maximum
    utilization of features provided by pytorch without reinventing the wheel.
    """
    def setup(self, *args, **kwargs):
        pass

    def forward(self, frames: InputType) -> InputType:
        pass

    def __init__(self):
        AbstractClassifierUDF.__init__(self)
        nn.Module.__init__(self)
        self.transforms = [transforms.ToTensor()]

    def get_device(self):
        return next(self.parameters()).device

    def transform(self, images: np.ndarray):
        composed = Compose(self.transforms)
        # reverse the channels from opencv
        return composed(Image.fromarray(images[:, :, ::-1])).unsqueeze(0)

    def forward(self, frames: List[np.ndarray]):
        tens_batch = torch.cat([self.transform(x) for x in frames]).to(
            self.get_device()
        )
        return self.classify(tens_batch)

    def classify(self, frames: Tensor) -> pd.DataFrame:
        """
        Given the gpu_batch_size, we split the input tensor inpto chunks.
        And call the _get_predictions and merge the results.
        Arguments:
            frames (Tensor): tensor on which transformation is performed
        Returns:
            pd.DataFrame: outcome after prediction
        """
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

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            return nn.Module.__call__(self, *args, **kwargs)

        frames = args[0]
        if isinstance(frames, pd.DataFrame):
            frames = frames.transpose().values.tolist()[0]

        return nn.Module.__call__(self, frames, **kwargs)


class PytorchAbstractTransformationUDF(AbstractTransformationUDF, Compose):
    """
    Use PyTorch torchvision transforms as EVA transforms.
    """

    def __init__(self, transforms):
        Compose.__init__(self, transforms)

    def transform(self, frames: ArrayLike) -> ArrayLike:
        return Compose.__call__(self, frames)

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            return nn.Module.__call__(self, *args, **kwargs)

        frames = args[0]
        if isinstance(frames, pd.DataFrame):
            frames = frames.transpose().values.tolist()[0]

        return Compose.__call__(self, frames, **kwargs)
