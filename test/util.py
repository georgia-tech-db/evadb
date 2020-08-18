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
import cv2
import os

from src.models.storage.batch import Batch
from src.parser.parser import Parser
from src.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from src.optimizer.plan_generator import PlanGenerator
from src.executor.plan_executor import PlanExecutor
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.udfs.abstract_udfs import AbstractClassifierUDF

NUM_FRAMES = 10


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


def custom_list_of_dicts_equal(one, two):
    for v1, v2 in zip(one, two):
        if v1.keys() != v2.keys():
            return False
        for key in v1.keys():
            if isinstance(v1[key], np.ndarray):
                if not np.array_equal(v1[key], v2[key]):
                    return False

            else:
                if v1[key] != v2[key]:
                    return False

    return True


def create_sample_video(num_frames=NUM_FRAMES):
    try:
        os.remove('dummy.avi')
    except FileNotFoundError:
        pass

    out = cv2.VideoWriter('dummy.avi',
                          cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                          (2, 2))
    for i in range(num_frames):
        frame = np.array(np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                         dtype=np.uint8)
        out.write(frame)


def create_dummy_batches(num_frames=NUM_FRAMES,
                         filters=[], batch_size=10, start_id=0):
    if not filters:
        filters = range(num_frames)
    data = []
    for i in filters:
        data.append({'id': i + start_id,
                     'data': np.array(
                         np.ones((2, 2, 3)) * 0.1 * float(i + 1) * 255,
                         dtype=np.uint8)})

        if len(data) % batch_size == 0:
            yield Batch(pd.DataFrame(data))
            data = []
    if data:
        yield Batch(pd.DataFrame(data))


def perform_query(query):
    stmt = Parser().parse(query)[0]
    l_plan = StatementToPlanConvertor().visit(stmt)
    p_plan = PlanGenerator().build(l_plan)
    return PlanExecutor(p_plan).execute_plan()


class DummyObjectDetector(AbstractClassifierUDF):

    @property
    def name(self) -> str:
        return "dummyObjectDetector"

    def __init__(self):
        super().__init__()

    @property
    def input_format(self):
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self):
        return ['__background__', 'person', 'bicycle']

    def classify(self, frames: np.ndarray):
        labels = [self.labels[i % 2 + 1] for i in range(len(frames))]
        prediction_df_list = pd.DataFrame({'label': labels})
        return prediction_df_list
