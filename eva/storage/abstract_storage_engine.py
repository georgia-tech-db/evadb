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
from typing import Iterator

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch


class AbstractStorageEngine(metaclass=ABCMeta):
    """
    Abstract class for defining storage engine. Storage engine is responsible
    for handling data storage and retrieval tasks.
    This contains a minimal set of APIs that each engine should implement

    """

    @abstractmethod
    def create(self, table: DataFrameMetadata):
        """Interface that implements all the necessary task required for
            creating the basic unit of storage(table or dataframe)

        Attributes:
            table: storage unit to be created
        """

    @abstractmethod
    def write(self, table: DataFrameMetadata, rows: Batch):
        """Interface responsible for inserting the rows into the required
        table. Internally calls the _open function and does the required
        task.

        Attributes:
            table: storage unit to be created
            rows : rows data to be written
        """

    @abstractmethod
    def read(
        self,
        table: DataFrameMetadata,
        batch_mem_size: int,
        predicate: AbstractExpression = None,
    ) -> Iterator[Batch]:
        """Interface responsible for yielding row/rows to the client.
        This should be implemeneted as an interator over of table. Helpful
        while doing full table scan. `pos` parameter is used if user wants
        to fetch specific rows.

        Attributes:
            table: storage unit to be read
            pos: row position to be returned

        Returns:
            Batch: an iterator of the batch read
        """
