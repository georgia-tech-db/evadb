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
from abc import ABCMeta, abstractmethod
from typing import TypeVar

GPUCompatible = TypeVar("GPUCompatible")


class GPUCompatible(metaclass=ABCMeta):
    @abstractmethod
    def to_device(self, device: str) -> GPUCompatible:
        """
        Implement this method to enable GPU for the function being executed.
        Arguments:
            device (str): device details

        Returns:
            A GPU compatible object
        """
