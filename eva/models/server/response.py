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
import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from eva.models.storage.batch import Batch


class ResponseStatus(str, Enum):
    FAIL = -1
    SUCCESS = 0


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Batch):
            return {"__batch__": obj.to_json()}
        return json.JSONEncoder.default(self, obj)


def as_response(d):
    if "__batch__" in d:
        return Batch.from_json(d["__batch__"])
    else:
        return d


@dataclass(frozen=True)
class Response:
    """
    Data model for EVA server response
    """

    status: ResponseStatus
    batch: Batch
    error: Optional[str] = None
    query_time: Optional[float] = None

    def to_json(self):
        obj = {"status": self.status, "batch": self.batch}
        if self.error is not None:
            obj["error"] = self.error
        if self.query_time is not None:
            obj["query_time"] = self.query_time

        return json.dumps(obj, cls=ResponseEncoder)

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str, object_hook=as_response)
        return cls(**obj)

    def __str__(self):
        if self.query_time is not None:
            return (
                "@status: %s\n"
                "@batch: %s\n"
                "@query_time: %s" % (self.status, self.batch, self.query_time)
            )
        else:
            return (
                "@status: %s\n"
                "@batch: %s\n"
                "@error: %s" % (self.status, self.batch, self.error)
            )
