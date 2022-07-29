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

from eva.readers.abstract_reader import AbstractReader
from eva.utils.logging_manager import logger


class CSVReader(AbstractReader):
    def __init__(self, *args, column_list, **kwargs):
        """
        Reads a CSV file and yields frame data.
        Args:
            column_list: list of columns (TupleValueExpression)
            to read from the CSV file
        """

        self._column_list = column_list
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:

        # TODO: What is a good location to put this code?
        def convert_csv_string_to_ndarray(row_string):
            """
            Conver a string of comma seperated values to a numpy
            float array
            """
            return np.array([np.float32(val) for val in row_string.split(",")])

        logger.info("Reading CSV frames")

        # TODO: Need to add strong sanity checks on the columns.

        # read the csv in chunks, and only keep the columns we need
        col_list_names = [col.col_name for col in self._column_list]
        col_map = {col.col_name: col for col in self._column_list}
        for chunk in pd.read_csv(self.file_url, chunksize=512, usecols=col_list_names):

            # apply the required conversions
            for col in chunk.columns:

                # TODO: Is there a better way to do this?
                if (
                    isinstance(chunk[col].iloc[0], str)
                    and col_map[col].col_object.type.name == "NDARRAY"
                ):

                    # convert the string to a numpy array
                    chunk[col] = chunk[col].apply(convert_csv_string_to_ndarray)

            # yield the chunk
            for chunk_index, chunk_row in chunk.iterrows():
                yield chunk_row
