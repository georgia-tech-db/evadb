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


# GLOBAL CONSTANTS 
_START_TIME = None
_END_TIME = None


def start_timer():
    global _START_TIME
    global _END_TIME

    _START_TIME = time.perf_counter_ns()


def end_timer():
    global _START_TIME
    global _END_TIME

    _END_TIME = time.perf_counter_ns()


def elapsed_time(context: str = None, report_time: bool = True):
    global _START_TIME
    global _END_TIME

    elapsed_time = (_END_TIME - _START_TIME) / 1000  # convert ns to ms
    if report_time is True:
        if context is None:
            logger.warn("elapsed time: {:0.4f} msec".format(elapsed_time))
        else:
            logger.warn("{:s}: {:0.4f} msec".format(context, elapsed_time))

    # Reset
    _START_TIME = None
    _END_TIME = None

    return elapsed_time
