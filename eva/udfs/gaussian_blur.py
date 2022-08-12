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

from torchvision import transforms as tv_transforms

from eva.udfs.pytorch_abstract_udf import PytorchAbstractTransformationUDF


class GaussianBlur(PytorchAbstractTransformationUDF, tv_transforms.GaussianBlur):
    def __init__(self, kernel_size: int = 3, sigma: float = 0.5):
        blur = tv_transforms.GaussianBlur(kernel_size=kernel_size, sigma=sigma)
        PytorchAbstractTransformationUDF.__init__(self, [blur])
