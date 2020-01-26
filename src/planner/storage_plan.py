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
from src.models.catalog.video_info import VideoMetaInfo
from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanNodeType


class StoragePlan(AbstractPlan):
    """
    This is the plan used for retrieving the frames from the storage and
    and returning to the higher levels.
    """

    def __init__(self, video: VideoMetaInfo, batch_size: int = 1,
                 skip_frames: int = 0, offset: int = None, limit: int = None):
        super().__init__(PlanNodeType.STORAGE_PLAN)
        self._video = video
        self._batch_size = batch_size
        self._skip_frames = skip_frames
        self._offset = offset
        self._limit = limit

    @property
    def video(self):
        return self._video

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def skip_frames(self):
        return self._skip_frames

    @property
    def offset(self):
        return self._offset

    @property
    def limit(self):
        return self._limit
