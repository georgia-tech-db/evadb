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

from typing import Any, Dict, List

from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.plan_nodes.types import PlanOprType


class ExchangePlan(AbstractPlan):
    """
    This plan is used for storing information required for union operations.

    Arguments:
        all: Bool
            UNION (deduplication) vs UNION ALL (non-deduplication)
    """

    def __init__(
        self,
        inner_plan: AbstractPlan,
        parallelism: int = 1,
        ray_pull_env_conf_dict: Dict[str, Any] = {},
        ray_parallel_env_conf_dict: List[Dict[str, Any]] = [{}],
    ):
        self.inner_plan = inner_plan
        self.parallelism = parallelism
        # Environment variables to configure in the remote process. The problem of Ray remote function
        # is that we cannot control which GPU to spawn the job. Second, Ray does not offer anything
        # extra when specify GPU job. Just by giving environment variables like CUDA_VISIBLE_DEVICES,
        # our system can have more control over the behavior of Ray.
        self.ray_parallel_env_conf_dict = ray_parallel_env_conf_dict
        self.ray_pull_env_conf_dict = ray_pull_env_conf_dict
        super().__init__(PlanOprType.EXCHANGE)

    def __str__(self) -> str:
        return "ExchangePlan"

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.inner_plan,
                self.parallelism,
            )
        )
