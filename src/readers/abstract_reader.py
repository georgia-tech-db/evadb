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
from abc import ABCMeta, abstractmethod
from typing import Iterator

from src.catalog.models.df_metadata import DataFrameMetadata
from src.models.storage.batch import FrameBatch
from src.models.storage.frame import Frame


class AbstractReader(metaclass=ABCMeta):
    """
    Abstract class for defining data reader. All other video readers use this
    abstract class. Video readers are expected to return data in an iterative manner.

    Attributes:
        file_url (str): path to read data from
        batch_size (int, optional): No. of frames to read in batch from video
        offset (int, optional): Start frame location in video
        """

    def __init__(self, file_url: str, batch_size=1,
                 offset=None):
        self.file_url = file_url
        self.batch_size = batch_size
        self.offset = offset

    def read(self):
        """
        This calls the sub class read implementation and
        yields the data to the caller
        """

        data_batch = []
        for data in self._read():
            data_batch.append(data)
            if len(data) % self.batch_size == 0:
                yield data_batch
                data_batch = []
        if data_batch:
            return data_batch

    @abstractmethod
    def _read(self):
        """
        Every sub class implements it's own logic
        to read the file and yield the data
        """
