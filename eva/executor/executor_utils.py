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

from eva.catalog.catalog_manager import CatalogManager
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch
from eva.parser.table_ref import TableInfo
from eva.utils.logging_manager import logger


class ExecutorError(Exception):
    pass


def apply_project(batch: Batch, project_list: List[AbstractExpression]):
    if not batch.empty() and project_list:
        batches = [expr.evaluate(batch) for expr in project_list]
        batch = Batch.merge_column_wise(batches)
    return batch


def apply_predicate(batch: Batch, predicate: AbstractExpression) -> Batch:
    if not batch.empty() and predicate is not None:
        outcomes = predicate.evaluate(batch)
        batch.drop_zero(outcomes)
        batch.reset_index()
    return batch


def handle_if_not_exists(table_info: TableInfo, if_not_exist=False):
    if CatalogManager().check_table_exists(
        table_info.database_name, table_info.table_name
    ):
        err_msg = "Table: {} already exists".format(table_info)
        if if_not_exist:
            logger.warn(err_msg)
            return True
        else:
            logger.error(err_msg)
            raise ExecutorError(err_msg)
    else:
        return False

def validate_image(image_path: Path) -> bool:
    try:
        data = cv2.imread(str(image_path))
        return data is not None
    except Exception as e:
        logger.warning(
            f"Unexpected Exception {e} occured while reading image file {image_path}"
        )
        return False