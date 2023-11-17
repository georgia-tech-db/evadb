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
import ast

import numpy as np
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_pytesseract


class PyTesseractOCRFunction(AbstractFunction):
    @property
    def name(self) -> str:
        return "PyTesseractOCRFunction"

    @setup(cacheable=False, function_type="FeatureExtraction", batchable=False)
    def setup(
        self, convert_to_grayscale: str, remove_noise: str, tesseract_path: str = None
    ) -> None:  # type: ignore
        try_to_import_pytesseract()

        # set the tesseract engine
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        self.grayscale_flag = convert_to_grayscale
        self.remove_noise = remove_noise

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT64],
                column_shapes=[(None, 3)],
            ),
        ],
        output_signatures=[
            PandasDataframe(
                columns=["text"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:
        img_data = np.asarray(frames["data"][0])

        if ast.literal_eval(self.grayscale_flag):
            img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)

        if ast.literal_eval(self.remove_noise):
            img_data = cv2.medianBlur(img_data, 5)

        # apply the OCR
        text = pytesseract.image_to_string(img_data)

        new_df = {"text": [text]}

        return pd.DataFrame(new_df)
