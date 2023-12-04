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
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_cv2


class BlobDetector(AbstractFunction):
    @setup(cacheable=False, function_type="cv2-transformation", batchable=True)
    def setup(self):
        try_to_import_cv2()

    @property
    def name(self):
        return "BlobDetector"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["num_labels", "labeled_im"],
                column_types=[NdArrayType.FLOAT32, NdArrayType.FLOAT32],
                column_shapes=[(None,), (None, None)],
            )
        ],
    )
    def forward(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        counting the blobs from a thresholded image

         Returns:
             ret (pd.DataFrame): The modified frame.
        """

        def blobdetector(row: pd.Series) -> np.ndarray:
            frame = row

            import cv2

            num_labels, labels_im = cv2.connectedComponents(frame)

            return num_labels, labels_im

        results = frame["data"].apply(blobdetector)
        ret = pd.DataFrame(results.tolist(), columns=["num_labels", "labeled_im"])
        return ret
