from typing import List

import pytest
import numpy as np

@pytest.fixture
def all_zeros_callable():
    """
    Operates on single frame and returns bool
    """
    def forward(frame: np.array) -> bool:
        return not np.any(frame)

    return forward

def test_zeros_callable_true(all_zeros_callable):
    # 4 x 4 frame with 3 channels
    frame = np.zeros((3, 4, 4))
    assert all_zeros_callable(frame)

def test_zeros_callable_mixed(all_zeros_callable):
    frame = np.array([0, 1, 2, 0])
    assert not all_zeros_callable(frame)

# @pytest.fixture
# def all_zeros_udf():
#     all_zero_udf = UDFService()

#     all_zero_udf.name = "all_zero_udf"

#     @all_zero_udf.setup
#     def setup():
#         pass

#     @all_zero_udf.forward(input_type=NdArray, channels_first=True, output_type=List[bool])
#     def forward(frames: np.array) -> bool:
#         return not np.any(frames, axis=4)

