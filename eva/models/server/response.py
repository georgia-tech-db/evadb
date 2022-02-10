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

    def __init__(self, status: ResponseStatus, batch: Batch, metrics=None):
        self._status = status
        self._batch = batch
        self._metrics = metrics

    def to_json(self):
        obj = {'status': self.status,
               'batch': self.batch,
               'metrics': self.metrics}
        return json.dumps(obj, cls=ResponseEncoder)

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str, object_hook=as_response)
        return cls(**obj)

    def __eq__(self, other: 'Response'):
        return self.status == other.status and \
            self.batch == other.batch and \
            self.metrics == other.metrics

    def __str__(self):
        return 'Response Object:\n' \
               '@status: %s\n' \
               '@batch: %s\n' \
               '@metrics: %s' \
               % (self.status, self.batch, self.metrics)

    @property
    def status(self):
        return self._status

    @property
    def batch(self):
        return self._batch

    @property
    def metrics(self):
        return self._metrics
