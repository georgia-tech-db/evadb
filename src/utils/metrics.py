import time


class MetricsManager(object):
    _timers = {}
    _order = []  # helps with nesting

    def start(self, context):
        if context in self._timers:
            raise Exception(
                f"context: '{context}' already exists in MetricsManager")

        self._timers[context] = {"start": time.time(), "children": {}}
        self._order.append(context)

    def end(self, context):
        if context not in self._timers:
            raise Exception(
                f"context: '{context}' does not exist in MetricsManager")

        self._timers[context]["end"] = time.time()
        self._order.append(context)

    def print(self):
        # todo generate meaningful string output from timers
        return self._timers


def mm_start(mm: MetricsManager, context: str):
    if mm is not None:
        mm.start(context)


def mm_end(mm: MetricsManager, context: str):
    if mm is not None:
        mm.end(context)


def mm_print(mm: MetricsManager):
    if mm is not None:
        mm.print()
