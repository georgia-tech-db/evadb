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

import numpy as np
import pandas as pd

from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.readers.abstract_reader import AbstractReader
from eva.utils.logging_manager import logger
from langchain.document_loaders import PyPDFLoader

class PDFReader(AbstractReader):
    def __init__(self, *args, **kwargs):
        """
        Reads a CSV file and yields frame data.
        Args:
            column_list: list of columns (TupleValueExpression)
            to read from the CSV file
        """

        # self._column_list = column_list
        super().__init__(*args, **kwargs)
        # self.table_df = pd.DataFrame(columns=['data',"file_path"])

    def _read(self) -> Iterator[Dict]:
        # TODO: What is a good location to put this code?

        loader = PyPDFLoader(self.file_url)
        # pages = loader.load_and_split()
        for data in loader.load():
            yield {"data": data.page_content,"file_path":str(self.file_url)}
        # for idx,val in enumerate(pages):
        #     self.table_df.loc[len(self.table_df.index)]=[val.page_content,str(self.file_url)+"_"+str(idx)]

        # for chunk_index, chunk_row in self.table_df.iterrows():
        #     yield chunk_row

        