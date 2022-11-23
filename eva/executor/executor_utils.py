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
from pathlib import Path
from typing import Generator, List

import cv2

from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch


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


def iter_path_regex(path_regex: Path) -> Generator[str, None, None]:
    return glob.iglob(os.path.expanduser(path_regex), recursive=True)


def validate_image(image_path: Path) -> bool:
    data = cv2.imread(str(image_path))
    return data is not None
