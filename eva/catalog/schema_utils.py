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
from typing import Dict, List

from sqlalchemy import TEXT, Column, Float, Integer, LargeBinary

from eva.catalog.column_type import ColumnType
from eva.catalog.models.df_column import DataFrameColumn
from eva.utils.logging_manager import logger


class SchemaUtils(object):
    @staticmethod
    def get_sqlalchemy_column(df_column: DataFrameColumn) -> Column:
        column_type = df_column.type

        sqlalchemy_column = None
        if column_type == ColumnType.INTEGER:
            sqlalchemy_column = Column(Integer)
        elif column_type == ColumnType.FLOAT:
            sqlalchemy_column = Column(Float)
        elif column_type == ColumnType.TEXT:
            sqlalchemy_column = Column(TEXT)
        elif column_type == ColumnType.NDARRAY:
            sqlalchemy_column = Column(LargeBinary)
        else:
            logger.error("Invalid column type: " + str(column_type))

        return sqlalchemy_column

    @staticmethod
    def get_sqlalchemy_schema(
        column_list: List[DataFrameColumn],
    ) -> Dict[str, Column]:
        """Converts the list of DataFrameColumns to SQLAlchemyColumns

        Args:
            column_list (List[DataFrameColumn]): columns to be converted

        Returns:
            Dict[str, Column]: mapping from column_name to sqlalchemy column object
        """
        return {
            column.name: SchemaUtils.get_sqlalchemy_column(column)
            for column in column_list
        }
