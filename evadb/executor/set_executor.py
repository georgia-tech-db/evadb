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
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.parser.set_statement import SetStatement


class SetExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: SetStatement):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        # Get method implementation from the config.update_value
        """
        NOTE :- Currently adding adding all configs in 'default' category.
        The idea is to deprecate category to maintain the same format for
        the query as DuckDB and Postgres

        Ref :-
        https://www.postgresql.org/docs/7.0/sql-set.htm
        https://duckdb.org/docs/sql/configuration.html

        This design change for configuation manager will be taken care of
        as a separate PR for the issue #1140, where all instances of config use
        will be replaced
        """
        self._config.update_value(
            category="default",
            key=self.node.config_name,
            value=self.node.config_value.value,
        )
