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
from test.util import create_sample_video, file_remove

import numpy as np
import pandas as pd
import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.udfs.udf_service import UDFService

NUM_FRAMES = 10


@pytest.fixture(scope="session")
def load_dummy_video():
    CatalogManager().reset()
    create_sample_video(NUM_FRAMES)
    load_query = """LOAD FILE 'dummy.avi' INTO MyVideo;"""
    execute_query_fetch_all(load_query)
    yield
    file_remove("dummy.avi")


@pytest.fixture(scope="session")
def dummy_object_detector():
    udf_service = UDFService(
        "DummyObjectDetector", labels=["__background__", "person", "bicycle"]
    )

    @udf_service.forward
    def forward(df: pd.DataFrame) -> pd.DataFrame:
        def classify_one(frames: np.ndarray):
            # odd are labeled bicycle and even person
            i = int(frames[0][0][0][0] * 25) - 1

            # TODO: replace with label instance in class
            label = ["__background__", "person", "bicycle"][i % 2 + 1]
            return np.array([label])

        ret = pd.DataFrame()
        ret["label"] = df.apply(classify_one, axis=1)
        return ret

    return udf_service.create_udf()


@pytest.fixture(scope="session")
def register_dummy_udf(load_dummy_video, dummy_object_detector):
    # TODO: update query to register decorator UDF
    create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
    return execute_query_fetch_all(create_udf_query)


def test_is_udf_classifier_instance(dummy_object_detector):
    assert issubclass(dummy_object_detector, AbstractClassifierUDF)


def test_udf_labels(dummy_object_detector):
    assert dummy_object_detector().labels == [
        "__background__",
        "person",
        "bicycle",
    ]
