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
from typing import Dict, Iterator

from eva.readers.abstract_reader import AbstractReader
from langchain.document_loaders import PyPDFLoader


class PDFReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        """
        Reads a CSV file and yields frame data.
        Args:
            column_list: list of columns (TupleValueExpression)
            to read from the CSV file
        """

        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        # TODO: What is a good location to put this code?

        loader = PyPDFLoader(self.file_url)
        for index, data in enumerate(loader.load()):
            yield {"page": index + 1, "data": data.page_content}
