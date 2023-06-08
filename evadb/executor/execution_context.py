# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from typing import List

from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.constants import NO_GPU
from evadb.utils.generic_utils import get_gpu_count, is_gpu_available


class Context:
    """
    Stores the context information of the executor, i.e.,
    if using spark, name of the application, current spark executors,
    if using horovod: current rank etc.
    """

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Context, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._config_manager = ConfigurationManager()
        self._gpus = self._populate_gpu_ids()

    @property
    def gpus(self):
        return self._gpus

    def _populate_gpu_from_config(self) -> List:
        # Populate GPU IDs from yaml config file.
        gpu_conf = self._config_manager.get_value("executor", "gpu_ids")
        available_gpus = [i for i in range(get_gpu_count())]
        return list(set(available_gpus) & set(gpu_conf))

    def _populate_gpu_from_env(self) -> List:
        # Populate GPU IDs from env variable.
        gpu_conf = map(
            lambda x: x.strip(),
            os.environ.get("CUDA_VISIBLE_DEVICES", "").strip().split(","),
        )
        gpu_conf = list(filter(lambda x: x, gpu_conf))
        gpu_conf = [int(gpu_id) for gpu_id in gpu_conf]
        available_gpus = [i for i in range(get_gpu_count())]
        return list(set(available_gpus) & set(gpu_conf))

    def _populate_gpu_ids(self) -> List:
        # Populate available GPU IDs from Torch library. Then, select subset of GPUs
        # from available GPUs based on user configuration.
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
