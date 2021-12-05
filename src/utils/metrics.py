import time


class MetricsManager(object):
    _timers = {}
    _current = ""  # helps with nesting

    def start(self, context):
        if self._current != "":
            self._current += f".{context}"
        else:
            self._current = context

        if self._current in self._timers:
            raise Exception(
                f"context: '{self._current}' already exists in MetricsManager")

        self._timers[self._current] = {"start": time.time(), "children": {}}

    def end(self, context):
        if not self._current.endswith(context):
            raise Exception(
                f"invalid context: '{context},"
                f" current context: '{self._current}")

        if self._current not in self._timers:
            raise Exception(
                f"context: '{self._current}' does not exist in MetricsManager")

        self._timers[self._current]["end"] = time.time()
        self._current = ".".join(self._current.split(".")[:-1])

    def print(self):
        # todo generate meaningful string output from timers
        return self._timers, self._current


def mm_start(mm: MetricsManager, context: str):
    if mm is not None:
        mm.start(context)


def mm_end(mm: MetricsManager, context: str):
    if mm is not None:
        mm.end(context)


def mm_print(mm: MetricsManager):
    if mm is not None:
        mm.print()
