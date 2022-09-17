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
import yaml
from typing import Any
from pathlib import Path

def read_value_config(config_path: Path, category: str, key: str) -> Any:
    with config_path.open("r") as yml_file:
        config_obj = yaml.load(yml_file)
        if config_obj is None:
            raise ValueError(f"Invalid path to config file {config_path}")
        return config_obj[category][key]


def update_value_config(config_path: Path, category: str, key: str, value: str):
    # read config file
    with config_path.open("r") as yml_file:
        config_obj = yaml.load(yml_file)
        if config_obj is None:
            raise ValueError(f"Invalid path to config file {config_path}")

    # update value and write back to config file
    config_obj[category][key] = value
    with config_path.open("w") as yml_file:
        yml_file.write(yaml.dump(config_obj))

