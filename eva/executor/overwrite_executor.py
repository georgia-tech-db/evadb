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
import cv2
import numpy as np
import os
import pandas as pd
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.parser.types import FileFormatType
from eva.plan_nodes.overwrite_plan import OverwritePlan
from eva.storage.storage_engine import StorageEngine


class OverwriteExecutor(AbstractExecutor):
    def __init__(self, node: OverwritePlan):
        super().__init__(node)
        self.catalog = CatalogManager()

    def exec(self, *args, **kwargs):
        table_info = self.node.table_info
        database_name = table_info.database_name
        table_name = table_info.table_name
        table_obj = self.catalog.get_table_catalog_entry(table_name, database_name)
        storage_engine = StorageEngine.factory(table_obj)
        batch_mem_size = 30000000
        operation = self.node.operation

        if table_obj.table_type == TableType.VIDEO_DATA:
            batches = storage_engine.read(table_obj, batch_mem_size)

            for batch in batches:
                video_paths = list(set(batch.frames['name']))

                new_video_paths = []
                for video_path in video_paths:
                    cap = cv2.VideoCapture(video_path)
                    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    video = np.empty((fc, fh, fw, 3), np.dtype('uint8'))

                    has_next = True
                    fn = 0
                    while has_next:
                        has_next, img = cap.read()
                        if has_next:
                            video[fn] = img
                        fn += 1

                    modified = None

                    # a MUX for operations
                    if operation == "flip-horizontal":
                        modified = np.flip(video, axis=2)
                    elif operation == "flip-vertical":
                        modified = np.flip(video, axis=1)

                    if modified is not None:
                        dirs = video_path.split('/')
                        dirs.append(dirs[-1])
                        dirs[-2] = 'modified'
                        modified_dir = '/'.join(dirs[:-1])
                        if not os.path.exists(modified_dir):
                            os.mkdir(modified_dir)
                        new_video_path = '/'.join(dirs)
                        new_video_paths.append(new_video_path)

                        out = cv2.VideoWriter(new_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fc, (fw, fh))
                        for fn in range(fc):
                            out.write(modified[fn])
                        out.release()
                    cap.release()

                storage_engine.clear(table_obj, video_paths)
                storage_engine.write(table_obj, Batch(pd.DataFrame({"file_path": new_video_paths})))

            yield Batch(
                pd.DataFrame(
                    {"Table successfully overwritten by: {}".format(operation)},
                    index=[0],
                )
            )
        else:
            yield Batch(
                pd.DataFrame(
                    {"Overwrite only supports video data for : {}".format(operation)},
                    index=[0],
                )
            )
