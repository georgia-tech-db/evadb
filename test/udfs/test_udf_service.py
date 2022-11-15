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

import numpy as np
import pytest

from eva.udfs.udf_service import UDFService


@pytest.fixture(scope="session")
def all_zeros_callable():
    """
    Operates on single frame and returns bool
    """

    def forward(frame: np.array) -> bool:
        return not np.any(frame)

    return forward


@pytest.fixture(scope="session")
def all_zeros_udf(all_zeros_callable):
    all_zero_udf = UDFService("all_zeros")

    @all_zero_udf.setup
    def setup():
        pass

    @all_zero_udf.forward
    def forward(frame):
        return all_zeros_callable(frame)

    return all_zero_udf.generate_udf_class()


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np.zeros((3, 4, 4)), True),
        (np.array([0, 1, 2, 0]), False),
        (np.ones((3, 4, 4)), False),
    ],
)
def test_zeros_callable(all_zeros_callable, test_input, expected):
    # 4 x 4 frame with 3 channels
    assert all_zeros_callable(test_input) == expected


def test_zeros_udf_name(all_zeros_udf):
    assert all_zeros_udf().name == "all_zeros"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (np.zeros((3, 4, 4)), True),
        (np.array([0, 1, 2, 0]), False),
        (np.ones((3, 4, 4)), False),
    ],
)
def test_zeros_udf_call(all_zeros_udf, test_input, expected):
    udf = all_zeros_udf()
    assert udf(test_input) == expected


def test_incomplete_udf():
    with pytest.raises(ValueError):
        UDFService("inc").generate_udf_class()
