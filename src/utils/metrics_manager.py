import time


class MetricsManager(object):
    def __init__(self):
        self._bandwidth = {}
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

    def bw_start(self, context: str):
        self._bandwidth[context] = {"time": time.time()}

    def bw_end(self, context: str, num_loaded_frames, file_size):
        if context not in self._bandwidth:
            raise Exception(
                f"context: '{context}' does not exist in MetricsManager")

        self._bandwidth[context]["time"] = time.time() - \
            self._bandwidth[context]["time"]
        self._bandwidth[context]["num_loaded_frames"] = num_loaded_frames
        self._bandwidth[context]["file_size_bytes"] = file_size

    def print(self):
        metrics = {"latency (ms)": self._prepare_latency()}

        if len(self._bandwidth) > 0:
            metrics["bandwidth"] = self._prepare_bandwidth()

        return metrics

    def _prepare_latency(self):
        latency = {}
        for k, v in self._timers.items():
            latency[k] = (v['end'] - v['start']) / 1000000  # convert ns to ms

        return latency

    def _prepare_bandwidth(self):
        bandwidth = {}

        for file, stats in self._bandwidth.items():
            load_rate_mem = (stats['file_size_bytes'] / 1024) / stats['time']
            load_rate_frames = stats['num_loaded_frames'] / stats['time']
            bandwidth[file] = f"{load_rate_mem:.2f} kb/s," \
                              f" {load_rate_frames:.2f} frames/s"

        return bandwidth


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


def mm_bw_start(mm: MetricsManager, context: str):
    if mm is not None:
        mm.bw_start(context)


def mm_bw_end(mm: MetricsManager, context: str, num_loaded_frames, file_size):
    if mm is not None:
        mm.bw_end(context, num_loaded_frames, file_size)


def mm_print(mm: MetricsManager):
    if mm is not None:
        mm.print()
