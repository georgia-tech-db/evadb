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
import pandas as pd
from pathlib import Path
from eva.planner.load_data_plan import LoadDataPlan
from eva.executor.abstract_executor import AbstractExecutor
from eva.storage.storage_engine import ImageStorageEngine
from eva.models.storage.batch import Batch
from eva.configuration.configuration_manager import ConfigurationManager


class LoadImageExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        self.upload_dir = Path(
            ConfigurationManager().get_value("storage", "upload_dir")
        )

    def validate(self):
        pass

    def exec(self):
        """ """
        image_file_path = None
        # Validate file_path
        if Path(self.node.file_path).exists():
            image_file_path = self.node.file_path
        # check in the upload directory
        else:
            image_path = Path(self.upload_path / self.node.file_path)
            if image_path.exists():
                image_file_path = image_path
        if image_file_path is None:
            error = "Failed to find the video file {}".format(
                self.node.file_path
            )

            raise RuntimeError(error)

        success = ImageStorageEngine.create(self.node.table_metainfo)

        if not success:
            raise RuntimeError("ImageStorageEngine create call failed")

        file_count = 0
        for file in image_file_path.iterdir():
            if file.is_file():
                if file.suffix in [".png", ".jpeg", ".jpg"]:
                    ImageStorageEngine.write(self.node.table_metainfo, file)
                    file_count += 1

        yield Batch(
            pd.DataFrame(
                {"Number of loaded images": str(file_count)}, index=[0]
            )
        )
