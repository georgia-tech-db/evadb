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
from pathlib import Path
from typing import Dict, Iterator

from evadb.readers.abstract_reader import AbstractReader
from evadb.readers.document.registry import _lazy_import_loader


class DocumentReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._LOADER_MAPPING = _lazy_import_loader()

    def _read(self) -> Iterator[Dict]:
        ext = Path(self.file_url).suffix
        assert ext in self._LOADER_MAPPING, f"File Format {ext} not supported"
        loader_class, loader_args = self._LOADER_MAPPING[ext]
        loader = loader_class(self.file_url, **loader_args)
        # load entire document as one entry
        # https://github.com/hwchase17/langchain/blob/d4fd58963885465fba70a5cea9554a7b043b02a1/langchain/schema.py#L269
        for data in loader.load():
            yield {"data": data.page_content}
