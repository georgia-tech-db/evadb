# coding=utf-8
# Copyright 2018-2023 EvaDB
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

import unittest

import pandas as pd
from mock import MagicMock

from evadb.third_party.huggingface.model import TextHFModel


class TestTextHFModel(TextHFModel):
    @property
    def default_pipeline_args(self) -> dict:
        # We need to improve the hugging face interface, passing
        # UdfCatalogEntry into UDF is not ideal.
        return {
            "task": "summarization",
            "model": "sshleifer/distilbart-cnn-12-6",
            "min_length": 5,
            "max_length": 100,
        }


class HuggingFaceTest(unittest.TestCase):
    def test_hugging_face_with_large_input(self):
        udf_obj = MagicMock()
        udf_obj.metadata = []
        text_summarization_model = TestTextHFModel(udf_obj)

        large_text = pd.DataFrame([{"text": "hello" * 4096}])
        try:
            text_summarization_model(large_text)
        except IndexError:
            self.fail("hugging face with large input raised IndexError.")
