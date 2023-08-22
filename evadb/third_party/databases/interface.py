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
import importlib
import os

import pip

INSTALL_CACHE = []


def get_database_handler(engine: str, **kwargs):
    """
    Return the database handler. User should modify this function for
    their new integrated handlers.
    """

    # Dynamically install dependencies.
    dynamic_install(engine)

    # Dynamically import the top module.
    mod = dynamic_import(engine)

    if engine == "postgres":
        return mod.PostgresHandler(engine, **kwargs)
    else:
        raise NotImplementedError(f"Engine {engine} is not supported")


def dynamic_install(handler_dir):
    """
    Dynamically install package from requirements.txt.
    """

    # Skip installation
    if handler_dir in INSTALL_CACHE:
        return

    INSTALL_CACHE.append(handler_dir)

    req_file = os.path.join(
        "evadb", "third_party", "databases", handler_dir, "requirements.txt"
    )
    if os.path.isfile(req_file):
        with open(req_file) as f:
            for package in f.read().splitlines():
                if hasattr(pip, "main"):
                    pip.main(["install", package])
                else:
                    pip._internal.main(["install", package])


def dynamic_import(handler_dir):
    import_path = f"evadb.third_party.databases.{handler_dir}.{handler_dir}_handler"
    return importlib.import_module(import_path)
