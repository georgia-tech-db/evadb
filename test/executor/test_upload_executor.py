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
import base64
import unittest
from pathlib import Path
from test.util import create_sample_csv_as_blob

from mock import mock_open, patch

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.upload_executor import UploadExecutor
from eva.parser.table_ref import TableInfo
from eva.parser.types import FileFormatType


class UploadExecutorTest(unittest.TestCase):
    def test_should_call_load_video_executor(self):
        file_path = "video"
        video_blob = "b'AAAA'"
        table_info = TableInfo("video")
        batch_mem_size = 3000
        file_options = {"file_format": FileFormatType.VIDEO}
        plan = type(
            "UploadPlan",
            (),
            {
                "file_path": file_path,
                "video_blob": video_blob,
                "table_info": table_info,
                "batch_mem_size": batch_mem_size,
                "file_options": file_options,
            },
        )

        with patch("builtins.open", mock_open()) as m:
            with patch(
                "eva.executor.upload_executor.LoadMultimediaExecutor", autospec=True
            ) as load_mock:
                load_mock.return_value.exec.return_value = iter([1, 2, 3])

                upload_executor = UploadExecutor(plan)
                next(upload_executor.exec())
                upload_dir = Path(
                    ConfigurationManager().get_value("storage", "upload_dir")
                )
                location = upload_dir / file_path
                m.assert_called_once_with(str(location), "wb")
                handle = m()
                video_bytes = base64.b64decode(video_blob[1:])
                handle.write.assert_called_once_with(video_bytes)

                load_mock.assert_called_once_with(plan)

    def test_should_call_load_csv_executor(self):
        # creates a dummy.csv
        csv_blob = create_sample_csv_as_blob()

        file_path = "dummy.csv"
        table_info = TableInfo("dummy")
        batch_mem_size = 3000
        file_options = {"file_format": FileFormatType.CSV}
        column_list = []
        plan = type(
            "UploadPlan",
            (),
            {
                "file_path": file_path,
                "video_blob": csv_blob,
                "table_info": table_info,
                "batch_mem_size": batch_mem_size,
                "column_list": column_list,
                "file_options": file_options,
            },
        )

        with patch("builtins.open", mock_open()) as m:
            with patch(
                "eva.executor.upload_executor.LoadCSVExecutor", autospec=True
            ) as load_mock:
                load_mock.return_value.exec.return_value = iter([1, 2, 3])

                upload_executor = UploadExecutor(plan)
                next(upload_executor.exec())
                upload_dir = Path(
                    ConfigurationManager().get_value("storage", "upload_dir")
                )
                location = upload_dir / file_path
                m.assert_called_once_with(str(location), "wb")
                handle = m()
                csv_bytes = base64.b64decode(csv_blob[1:])
                handle.write.assert_called_once_with(csv_bytes)

                load_mock.assert_called_once_with(plan)
