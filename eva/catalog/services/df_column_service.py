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
from typing import List

from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.models.df_column import DataFrameColumn
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.catalog.services.base_service import BaseService


class DatasetColumnService(BaseService):
    def __init__(self):
        super().__init__(DataFrameColumn)

    def columns_by_dataset_id_and_names(self, dataset_id, column_names):
        result = self.model.query.filter(
            self.model._metadata_id == dataset_id,
            self.model._name.in_(column_names),
        ).all()

        return result

    def columns_by_id_and_dataset_id(self, dataset_id: int, id_list: List[int] = None):
        """return all the columns that matches id_list and  dataset_id

        Arguments:
            dataset_id {int} -- [metadata id of the table]
            id_list {List[int]} -- [metadata ids of the required columns: If
            None return all the columns that matches the dataset_id]

        Returns:
            List[self.model] -- [the filtered self.models]
        """
        if id_list is not None:
            return self.model.query.filter(
                self.model._metadata_id == dataset_id,
                self.model._id.in_(id_list),
            ).all()

        return self.model.query.filter(self.model._metadata_id == dataset_id).all()

    def create_column(self, column_list):
        saved_column_list = []
        for column in column_list:
            saved_column_list.append(column.save())
        return saved_column_list

    def get_dataset_columns(self, dataset: DataFrameMetadata) -> List[DataFrameColumn]:
        try:
            return self.model.query.filter(self.model._metadata_id == dataset.id).all()
        except NoResultFound:
            return None
