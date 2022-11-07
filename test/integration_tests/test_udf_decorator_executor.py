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
import pandas as pd
import pytest

from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.udfs.udf_service import UDFService

# from test.util import file_remove


@pytest.fixture(scope="session")
def dummy_object_detector_service():
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

    yield udf_service.create_udf()

    # TODO: handle cleanup after writing tests which call UDF
    # file_remove("dummy.avi")


def test_is_udf_classifier_instance(dummy_object_detector_service):
    assert issubclass(dummy_object_detector_service, AbstractClassifierUDF)


def test_udf_labels(dummy_object_detector_service):
    assert dummy_object_detector_service().labels == [
        "__background__",
        "person",
        "bicycle",
    ]
