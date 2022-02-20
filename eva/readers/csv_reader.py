# coding=utf-8
# Copyright 2018-2020 EVA
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

import pandas as pd
from typing import Iterator, Dict

from eva.readers.abstract_reader import AbstractReader
from eva.utils.logging_manager import LoggingLevel
from eva.utils.logging_manager import LoggingManager


class CSVReader(AbstractReader):

    def __init__(self, *args, converters, column_list, **kwargs):
        """
            Reads a CSV file and yields frame data.

            Attributes:
                converters (dict): dictionary of converters to be used
                                    while loading the CSV file.
                column_list (list): list of columns to be read 
                                    from the CSV file.
        """

        self._converters = converters
        self._column_list = column_list
        super().__init__(*args, **kwargs)

    def _read(self) -> Iterator[Dict]:
        
        LoggingManager().log("Reading CSV frames", LoggingLevel.INFO)

        df = pd.read_csv(self.file_url, converters=self._converters)
        for index, row in df.iterrows():
            result = {}
            for column in self._column_list:
                result[column] = row[column]

            yield result