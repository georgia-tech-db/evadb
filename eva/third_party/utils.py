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
from eva.catalog.models.udf_catalog import UdfCatalogEntry


def get_metadata_entry(udf_obj: UdfCatalogEntry, key: str) -> (str, str):
    entry_found = False
    for metadata in udf_obj.metadata:
        if metadata.key == key:
            entry_found = True
            return key, metadata.value
    assert entry_found, f"{key} is not defined for {udf_obj.name}"
