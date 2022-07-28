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
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Dict, Iterator

import pandas as pd

from eva.models.storage.batch import Batch
from eva.utils.generic_utils import get_size


class AbstractReader(metaclass=ABCMeta):
    """
    Abstract class for defining data reader. All other video readers use this
    abstract class. Video readers are expected to return Batch
    in an iterative manner.

    Attributes:
        file_url (str): path to read data from
        batch_mem_size (int): used to compute the #frames to
                                            read in batch from video
        offset (int, optional): Start frame location in video
    """

    def __init__(self, file_url: str, batch_mem_size: int, offset=None):
        # Opencv doesn't support pathlib.Path so convert to raw str
        if isinstance(file_url, Path):
            file_url = str(file_url)
        self.file_url = file_url
        self.batch_mem_size = batch_mem_size
        self.offset = offset

    def read(self) -> Iterator[Batch]:
        """
        This calls the sub class read implementation and
        yields the batch to the caller
        """

        data_batch = []
        row_size = None
        for data in self._read():
            if row_size is None:
                row_size = 0
                row_size = get_size(data)
            data_batch.append(data)
            if len(data_batch) * row_size >= self.batch_mem_size:
                yield Batch(pd.DataFrame(data_batch))
                data_batch = []
        if data_batch:
            yield Batch(pd.DataFrame(data_batch))

    @abstractmethod
    def _read(self) -> Iterator[Dict]:
        """
        Every sub class implements it's own logic
        to read the file and yields an object iterator.
        """
