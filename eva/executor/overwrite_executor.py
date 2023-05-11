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
import os
from collections import defaultdict

import cv2
import numpy as np
import pandas as pd
from PIL import Image as im

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.executor.abstract_executor import AbstractExecutor
from eva.expression.function_expression import FunctionExpression
from eva.models.storage.batch import Batch
from eva.plan_nodes.overwrite_plan import OverwritePlan
from eva.storage.storage_engine import StorageEngine


class OverwriteExecutor(AbstractExecutor):
    def __init__(self, node: OverwritePlan):
        super().__init__(node)
        self.catalog = CatalogManager()
        self.table_ref = self.node.table_ref
        self.operation = self.node.operation

    def make_new_video_path(self, video_path: str):
        dirs = video_path.split("/")
        dirs.append(dirs[-1])
        dirs[-2] = "modified"
        modified_dir = "/".join(dirs[:-1])
        if not os.path.exists(modified_dir):
            os.mkdir(modified_dir)
        new_video_path = "/".join(dirs)
        return new_video_path

    def make_new_image_path(self, image_path: str):
        dirs = image_path.split("/")
        dirs[-1] = "modified_" + dirs[-1]

        new_image_path = "/".join(dirs)
        return new_image_path

    def exec(self, *args, **kwargs):
        assert type(self.operation) == FunctionExpression

        table_obj = self.table_ref.table.table_obj
        storage_engine = StorageEngine.factory(table_obj)
        batch_mem_size = 30000000

        if table_obj.table_type == TableType.VIDEO_DATA:
            batches = storage_engine.read(table_obj, batch_mem_size)
            modified_paths = dict()
            all_video_paths = set()
            all_videos = dict()

            for batch in batches:
                original_fc = batch.frames.shape[0]
                video_fc = defaultdict(lambda: 0)
                all_video_paths = all_video_paths.union(set(batch.frames["name"]))
                video_paths = list(set(batch.frames["name"]))
                for i in range(original_fc):
                    video_fc[batch.frames["name"][i]] += 1

                batch.modify_column_alias(self.table_ref.alias)
                res = self.operation.evaluate(batch)
                modified_frames = res.frames.iloc[:, 0].to_numpy()
                fc = modified_frames.shape[0]
                fh = modified_frames[0].shape[0]
                fw = modified_frames[0].shape[1]
                batch.drop_column_alias()

                assert original_fc == fc

                videos = dict()
                next_index = defaultdict(lambda: 0)

                for video_path in video_paths:
                    videos[video_path] = np.empty(
                        (video_fc[video_path], fh, fw, 3), np.dtype("uint8")
                    )
                    modified_paths[video_path] = self.make_new_video_path(video_path)

                for i in range(fc):
                    video_path = batch.frames["name"][i]
                    index = next_index[video_path]
                    videos[video_path][index] = modified_frames[i]
                    next_index[video_path] += 1

                for original_video_path in video_paths:
                    if original_video_path not in all_videos.keys():
                        all_videos[original_video_path] = videos[original_video_path]
                    else:
                        all_videos[original_video_path] = np.vstack(
                            (
                                all_videos[original_video_path],
                                videos[original_video_path],
                            )
                        )

            storage_engine.clear(table_obj, list(all_video_paths))
            all_modified_video_paths = []
            for original_video_path in list(all_video_paths):
                fc, fh, fw, _ = all_videos[original_video_path].shape
                out = cv2.VideoWriter(
                    modified_paths[original_video_path],
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    fc,
                    (fw, fh),
                )
                all_modified_video_paths.append(modified_paths[original_video_path])
                for fn in range(fc):
                    frame = all_videos[original_video_path][fn]
                    out.write(frame)
                out.release()

            storage_engine.write(
                table_obj, Batch(pd.DataFrame({"file_path": all_modified_video_paths}))
            )

            yield Batch(
                pd.DataFrame(
                    {
                        "Table successfully overwritten by: {}".format(
                            self.operation.name
                        )
                    },
                    index=[0],
                )
            )
        elif table_obj.table_type == TableType.IMAGE_DATA:
            batches = storage_engine.read(table_obj)
            modified_image_paths = []
            for batch in batches:
                image_paths = list(batch.frames["name"])

                batch.modify_column_alias(self.table_ref.alias)
                res = self.operation.evaluate(batch)
                modified_images = res.frames.iloc[:, 0].to_numpy()
                batch.drop_column_alias()

                for i in range(len(modified_images)):
                    image_path = image_paths[i]
                    modified_image_path = self.make_new_image_path(image_path)
                    modified_image_paths.append(modified_image_path)
                    data = im.fromarray(modified_images[i])
                    data.save(modified_image_path)

            storage_engine.clear(table_obj, image_paths)
            storage_engine.write(
                table_obj, Batch(pd.DataFrame({"file_path": modified_image_paths}))
            )

            yield Batch(
                pd.DataFrame(
                    {
                        "Table successfully overwritten by: {}".format(
                            self.operation.name
                        )
                    },
                    index=[0],
                )
            )
        else:
            yield Batch(
                pd.DataFrame(
                    {
                        "Overwrite only supports video data for : {}".format(
                            self.operation.name
                        )
                    },
                    index=[0],
                )
            )
