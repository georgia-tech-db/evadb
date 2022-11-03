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

import functools
from enum import Enum, auto
from typing import Callable

from numpy.typing import ArrayLike


class FrameType(Enum):
    NdArray = auto()
    PdDataFrame = auto()


class UDFService:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def setup(self, func: Callable):
        @functools.wraps(func)
        def wrapper_setup(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper_setup

    def forward(
        self,
        input_type: FrameType,
        output_type: FrameType,
        channels_first: bool = True,
        batch: bool = False,
    ):
        def decorator_forward(func: Callable):
            @functools.wraps(func)
            def wrapper_forward(frame: ArrayLike):
                return func(frame)

            return wrapper_forward

        return decorator_forward
