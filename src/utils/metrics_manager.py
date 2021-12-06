import time


class MetricsManager(object):
    def __init__(self):
        self._timers = {}
        self._current = ""  # helps with nesting

    def start(self, context):
        if self._current != "":
            self._current += f".{context}"
        else:
            self._current = context

        if self._current in self._timers:
            raise Exception(
                f"context: '{self._current}' already exists in MetricsManager")

        self._timers[self._current] = {"start": time.time_ns()}

    def end(self, context):
        if not self._current.endswith(context):
            raise Exception(
                f"invalid context: '{context},"
                f" current context: '{self._current}")

        if self._current not in self._timers:
            raise Exception(
                f"context: '{self._current}' does not exist in MetricsManager")

        self._timers[self._current]["end"] = time.time_ns()

        self._current = self._current[:-len(context)]
        if self._current.endswith("."):
            self._current = self._current[:-1]

    def print(self):
        latency = {}
        for k, v in self._timers.items():
            latency[k] = (v['end'] - v['start']) / 1000000  # convert ns to ms

        return {"latency (ms)": latency}


def mm_start(mm: MetricsManager, context: str):
    if mm is not None:
        mm.start(context)


def mm_end(mm: MetricsManager, context: str):
    if mm is not None:
        mm.end(context)


def mm_end_start(mm: MetricsManager, end: str, start: str):
    if mm is not None:
        mm.end(end)
        mm.start(start)


def mm_print(mm: MetricsManager):
    if mm is not None:
        mm.print()
