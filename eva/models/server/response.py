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
from enum import Enum

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


class Response:
    """
    Data model for EVA server response
    """

    def __init__(
        self,
        status: ResponseStatus,
        batch: Batch,
        error: str = "",
        query_time: float = None,
    ):
        self._status = status
        self._batch = batch
        self._error = error
        self._query_time = query_time

    def to_json(self):
        obj = {"status": self._status, "batch": self._batch}
        if self._error != "":
            obj["error"] = self._error
        if self._query_time is not None:
            obj["query_time"] = self._query_time

        return json.dumps(obj, cls=ResponseEncoder)

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str, object_hook=as_response)
        return cls(**obj)

    def __eq__(self, other: "Response"):
        return (
            self._status == other._status
            and self._batch == other._batch
            and self._error == other._error
            and self._query_time == other._query_time
        )

    def __str__(self):
        if self._query_time is not None:
            return (
                "@status: %s\n"
                "@batch: %s\n"
                "@query_time: %s" % (self._status, self._batch, self._query_time)
            )
        else:
            return (
                "@status: %s\n"
                "@batch: %s\n"
                "@error: %s" % (self._status, self._batch, self._error)
            )

    @property
    def status(self):
        return self._status

    @property
    def batch(self):
        return self._batch

    @property
    def error(self):
        return self._error

    @property
    def query_time(self):
        return self._query_time
