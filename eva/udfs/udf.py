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
from turtle import forward
from typing import List

import pandas as pd
from numpy.typing import ArrayLike

from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace

from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd
import torch
from numpy.typing import ArrayLike
from PIL import Image
from torch import Tensor, nn
from torchvision.transforms import Compose, transforms

from eva.configuration.configuration_manager import ConfigurationManager
from eva.udfs.abstract_udf import AbstractClassifierUDF
from eva.udfs.gpu_compatible import GPUCompatible


class UDF(AbstractClassifierUDF, nn.Module, GPUCompatible):
    """
    Class for all UDFs.

    TODO: We might need to store the labels somewhere
    """

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


    @property
    def name(self) -> str:
        return str(self)
    
    def _get_predictions(self, frames: Tensor) -> pd.DataFrame:
        print("Inside Get Predictions Method")
        predictions = self.model(frames)
        print(predictions)
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

    def classify(self, frames: Tensor) -> pd.DataFrame:
        print("Starting the classify method")
        gpu_batch_size = ConfigurationManager().get_value("executor", "gpu_batch_size")
        print(gpu_batch_size)
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
        pass
        # print("Entered the UDF call method")
        # if len(args) == 0:
        #     return nn.Module.__call__(self, *args, **kwargs)
        # frames = args[0]
        # if isinstance(frames, pd.DataFrame):
        #     frames = frames.transpose().values.tolist()[0]

        # return nn.Module.__call__(self, frames, **kwargs)

    def get_device(self):
        return next(self.parameters()).device