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
import numpy as np
import pandas as pd


def create_dataframe(num_frames=1) -> pd.DataFrame:
    frames = []
    for i in range(1, num_frames + 1):
        frames.append({"id": i, "data": (i * np.ones((1, 1)))})
    return pd.DataFrame(frames)


def create_dataframe_same(times=1):
    base_df = create_dataframe()
    for i in range(1, times):
        base_df = base_df.append(create_dataframe())

    return base_df
