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

color = (207, 248, 64)
thickness = 4


class Annotate(AbstractUDF):
    @setup(cacheable=False, udf_type="cv2-transformation", batchable=True)
    def setup(self):
        pass

    @property
    def name(self):
        return "Annotate"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data", "labels", "bboxes"],
                column_types=[
                    NdArrayType.FLOAT32,
                    NdArrayType.STR,
                    NdArrayType.FLOAT32,
                ],
                column_shapes=[(None, None, 3), (None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["annotated_frame_array"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Modify the frame to annotate the bbox on it.

         Returns:
             ret (pd.DataFrame): The modified frame.
        """

        def annotate(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]
            bboxes = row[2]
            try_to_import_cv2()
            import cv2

            for bbox in bboxes:
                x1, y1, x2, y2 = np.asarray(bbox, dtype="int")
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                frame = cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            return frame

        ret = pd.DataFrame()
        ret["annotated_frame_array"] = df.apply(annotate, axis=1)
        return ret
