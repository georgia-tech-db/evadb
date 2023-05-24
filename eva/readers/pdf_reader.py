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
import fitz


class PDFReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        """
        Reads a PDF file and yields frame data.
        Args:
            column_list: list of columns (TupleValueExpression)
            to read from the PDF file
        """

        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        # TODO: What is a good location to put this code?
        doc = fitz.open(self.file_url)

        for page_no, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for paragraph_no, b in enumerate(blocks):  # iterate through the text blocks
                if b['type'] == 0:  # this block contains text
                    block_string = ""  # text found in block
                    for lines in b["lines"]:  # iterate through the text lines
                        for span in lines["spans"]:  # iterate through the text spans
                            if span['text'].strip():  # removing whitespaces:
                                    block_string += span['text']
                    yield {"page": page_no + 1, "paragraph":paragraph_no + 1, "data": block_string}
