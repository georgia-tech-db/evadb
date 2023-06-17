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
import numpy as np
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_cv2


class ToGrayscale(AbstractUDF):
    @setup(cacheable=False, udf_type="cv2-transformation", batchable=True)
    def setup(self):
        try_to_import_cv2()

    @property
    def name(self):
        return "ToGrayscale"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["grayscale_frame_array"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
    )
    def forward(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the frame from BGR to grayscale

         Returns:
             ret (pd.DataFrame): The modified frame.
        """

        def toGrayscale(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]

            import cv2

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

            return frame

        ret = pd.DataFrame()
        ret["grayscale_frame_array"] = frame.apply(toGrayscale, axis=1)
        return ret
