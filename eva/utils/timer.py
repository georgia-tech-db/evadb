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

import time

from eva.utils.logging_manager import logger


class Timer:
    """Class used for logging time metrics.

    This is not thread safe"""

    def __init__(self):
        self._start_time = None
        self._total_time = 0.0

    def __enter__(self):
        assert self._start_time is None, "Concurrent calls are not supported"
        self._start_time = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._start_time is not None, "exit called with starting the context"
        time_elapsed = time.perf_counter() - self._start_time
        self._total_time += time_elapsed
        self._start_time = None

    @property
    def total_elapsed_time(self):
        return self._total_time

    def log_elapsed_time(self, context: str):
        logger.info("{:s}: {:0.4f} sec".format(context, self.total_elapsed_time))
