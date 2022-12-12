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
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from eva.models.storage.batch import Batch
from eva.utils.generic_utils import PickleSerializer


class ResponseStatus(str, Enum):
    FAIL = -1
    SUCCESS = 0


@dataclass(frozen=True)
class Response:
    """
    Data model for EVA server response
    """

    status: ResponseStatus
    batch: Batch
    error: Optional[str] = None
    query_time: Optional[float] = None

    def serialize(self):
        return PickleSerializer.serialize(self)

    @classmethod
    def deserialize(cls, data):
        obj = PickleSerializer.deserialize(data)
        return obj

    def __str__(self):
        if self.query_time is not None:
            return (
                "@status: %s\n"
                "@batch: \n %s\n"
                "@query_time: %s" % (self.status, self.batch, self.query_time)
            )
        else:
            return (
                "@status: %s\n"
                "@batch: \n %s\n"
                "@error: %s" % (self.status, self.batch, self.error)
            )
