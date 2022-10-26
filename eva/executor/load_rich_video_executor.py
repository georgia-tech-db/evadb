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
from pathlib import Path

import pandas as pd
import eva.utils.audio_utils as audio_utils

from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.executor.load_video_executor import LoadVideoExecutor
from eva.planner.load_data_plan import LoadDataPlan


class LoadRichVideoExecutor(LoadVideoExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)

    def exec(self):
        # TODO: super exec not creating table if it doesn't exist
        if super().exec() is not None:

            # TODO: make results typed
            catalog = CatalogManager()
            results = audio_utils.transcribe_file_with_word_time_offsets(self.node.file_path)
            for result in results:
                catalog.create_transcript_metadata(str(self.node.file_path), result['word'], result['start'], result['end'], result['conf'])

            yield Batch(
                pd.DataFrame(
                    [f"Rich video successfully added at location: {self.node.file_path}"]
                )
            )

