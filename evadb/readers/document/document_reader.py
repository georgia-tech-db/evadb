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

from evadb.catalog.sql_config import ROW_NUM_COLUMN
from evadb.configuration.constants import (
    DEFAULT_DOCUMENT_CHUNK_OVERLAP,
    DEFAULT_DOCUMENT_CHUNK_SIZE,
)
from evadb.readers.abstract_reader import AbstractReader
from evadb.readers.document.registry import (
    _lazy_import_loader,
    _lazy_import_text_splitter,
)


class DocumentReader(AbstractReader):
    def __init__(self, *args, chunk_params, **kwargs):
        super().__init__(*args, **kwargs)
        self._LOADER_MAPPING = _lazy_import_loader()
        self._splitter_class = _lazy_import_text_splitter()

        # https://github.com/hwchase17/langchain/blob/5b6bbf4ab2a33ed0d33ff5d3cb3979a7edc15682/langchain/text_splitter.py#L570
        # by default we use chunk_size 4000 and overlap 200
        self._chunk_size = chunk_params.get("chunk_size", DEFAULT_DOCUMENT_CHUNK_SIZE)
        self._chunk_overlap = chunk_params.get(
            "chunk_overlap", DEFAULT_DOCUMENT_CHUNK_OVERLAP
        )

    def _read(self) -> Iterator[Dict]:
        ext = Path(self.file_url).suffix
        assert ext in self._LOADER_MAPPING, f"File Format {ext} not supported"
        loader_class, loader_args = self._LOADER_MAPPING[ext]
        loader = loader_class(self.file_url, **loader_args)

        # todo: implement out own splitter
        langchain_text_splitter = self._splitter_class(
            chunk_size=self._chunk_size, chunk_overlap=self._chunk_overlap
        )

        row_num = 0
        for data in loader.load():
            for chunk_id, row in enumerate(
                langchain_text_splitter.split_documents([data])
            ):
                yield {
                    "chunk_id": chunk_id,
                    "data": row.page_content,
                    ROW_NUM_COLUMN: row_num,
                }
                row_num += 1
