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
from typing import Dict, Iterator

from evadb.readers.abstract_reader import AbstractReader
from evadb.utils.generic_utils import try_to_import_fitz


class PDFReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        """
        Reads a PDF file and yields frame data.
        Args:
            column_list: list of columns (TupleValueExpression)
            to read from the PDF file
        """
        super().__init__(*args, **kwargs)
        try_to_import_fitz()

    def _read(self) -> Iterator[Dict]:
        import fitz

        doc = fitz.open(self.file_url)

        # PAGE ID, PARAGRAPH ID, STRING
        for page_no, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            # iterate through the text blocks
            for paragraph_no, b in enumerate(blocks):
                # this block contains text
                if b["type"] == 0:
                    # text found in block
                    block_string = ""
                    # iterate through the text lines
                    for lines in b["lines"]:
                        # iterate through the text spans
                        for span in lines["spans"]:
                            # removing whitespaces:
                            if span["text"].strip():
                                block_string += span["text"]
                    yield {
                        "page": page_no + 1,
                        "paragraph": paragraph_no + 1,
                        "data": block_string,
                    }
