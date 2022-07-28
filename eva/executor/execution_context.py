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
import os
import random
import socket
from typing import List, Set

from eva.configuration.configuration_manager import ConfigurationManager
from eva.constants import NO_GPU
from eva.utils.generic_utils import is_gpu_available


class Context:
    """
    Stores the context information of the executor, i.e.,
    if using spark, name of the application, current spark executors,
    if using horovod: current rank etc.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Context, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._config_manager = ConfigurationManager()
        self._gpus = self._populate_gpu_ids()

    @property
    def gpus(self):
        return self._gpus

    def _possible_addresses(self) -> Set:
        host = socket.gethostname()
        result_address = {host}
        true_host, aliases, address = socket.gethostbyaddr(host)
        result_address.add(true_host)
        result_address.update(set(aliases).union(set(address)))
        return result_address

    def _populate_gpu_from_config(self) -> List:
        gpu_conf = self._config_manager.get_value("executor", "gpus")
        gpu_conf = gpu_conf if gpu_conf else {}
        this_address = self._possible_addresses()
        intersection_addresses = this_address.intersection(gpu_conf.keys())
        if len(intersection_addresses) != 0:
            return [str(gpu) for gpu in gpu_conf.get(intersection_addresses.pop())]
        return []

    def _populate_gpu_from_env(self) -> List:
        gpus = map(
            lambda x: x.strip(), os.environ.get("GPU_DEVICES", "").strip().split(",")
        )
        return list(filter(lambda x: x, gpus))

    def _populate_gpu_ids(self) -> List:
        if not is_gpu_available():
            return []
        gpus = self._populate_gpu_from_config()
        if len(gpus) == 0:
            gpus = self._populate_gpu_from_env()
        return gpus

    def _select_random_gpu(self) -> str:
        """
        A random GPU selection strategy
        Returns:
            (str): GPU device ID
        """
        return random.choice(self.gpus)

    def gpu_device(self) -> str:
        """
        Selects a GPU on which the task can be executed
        Returns:
             (str): GPU device ID
        """
        if self.gpus:
            # TODO: Should allow choosing GPU based on Spark and Horovod
            return self._select_random_gpu()
        return NO_GPU
