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
import glob
import os
import ray
from pathlib import Path
from typing import Generator, List

import cv2

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.execution_context import Context
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch
from eva.parser.table_ref import TableInfo
from eva.parser.types import FileFormatType
from eva.utils.logging_manager import logger


class ExecutorError(Exception):
    pass


def apply_project(batch: Batch, project_list: List[AbstractExpression]):
    if not batch.empty() and project_list:
        batches = [expr.evaluate(batch) for expr in project_list]
        batch = Batch.merge_column_wise(batches)
    return batch

@ray.remote
def apply_predicate_remote(batch: Batch, predicate: AbstractExpression) -> Batch:
    if not batch.empty() and predicate is not None:
        outcomes = predicate.evaluate(batch)
        batch.drop_zero(outcomes)
    return batch


def apply_predicate(batch: Batch, predicate: AbstractExpression) -> Batch:
    if not batch.empty() and predicate is not None:
        outcomes = predicate.evaluate(batch)
        batch.drop_zero(outcomes)
    return batch


def apply_predicate_distributed(batches: List[Batch], predicate: AbstractExpression, ray_parallelism: int) -> List[Batch]:
    output_batches = []
    ray_tasks = []
    ray_config = {"num_gpus": len(Context().gpus)/ray_parallelism} if Context().gpus else {"num_cpus": 1/ray_parallelism}
    for batch in batches:
        ray_tasks.append(apply_predicate_remote.options(**ray_config).remote(batch, predicate))
    output_batches = ray.get(ray_tasks)
    return output_batches


def handle_if_not_exists(table_info: TableInfo, if_not_exist=False):
    # Table exists
    if CatalogManager().check_table_exists(
        table_info.table_name,
        table_info.database_name,
    ):
        err_msg = "Table: {} already exists".format(table_info)
        if if_not_exist:
            logger.warn(err_msg)
            return True
        else:
            logger.error(err_msg)
            raise ExecutorError(err_msg)
    # Table does not exist
    else:
        return False


def validate_image(image_path: Path) -> bool:
    try:
        data = cv2.imread(str(image_path))
        return data is not None
    except Exception as e:
        logger.warning(
            f"Unexpected Exception {e} occurred while reading image file {image_path}"
        )
        return False


def iter_path_regex(path_regex: Path) -> Generator[str, None, None]:
    return glob.iglob(os.path.expanduser(path_regex), recursive=True)


def validate_video(video_path: Path) -> bool:
    try:
        vid = cv2.VideoCapture(str(video_path))
        if not vid.isOpened():
            return False
        return True
    except Exception as e:
        logger.warning(
            f"Unexpected Exception {e} occurred while reading video file {video_path}"
        )


def validate_media(file_path: Path, media_type: FileFormatType) -> bool:
    if media_type == FileFormatType.VIDEO:
        return validate_video(file_path)
    elif media_type == FileFormatType.IMAGE:
        return validate_image(file_path)
    else:
        raise ValueError(f"Unsupported Media type {str(media_type)}")
