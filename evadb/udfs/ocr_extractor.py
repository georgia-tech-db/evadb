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

import re

import numpy as np
import pandas as pd

from evadb.catalog.catalog_type import NdArrayType
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.udfs.gpu_compatible import GPUCompatible
from evadb.utils.generic_utils import (
    try_to_import_torch,
    try_to_import_donutmodel
)


class OCRExtractor(AbstractUDF, GPUCompatible):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        try_to_import_torch()
        try_to_import_torchvision()
        try_to_import_donutmodel()
        import torch
        from donut import DonutModel

        self.task_prompt="<s_cord-v2>"
        self.pretrained_model = DonutModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
        if torch.cuda.is_available():
            self.pretrained_model.half()
            device = torch.device("cuda")
            self.pretrained_model.to(device)
        else:
            self.pretrained_model.encoder.to(torch.float)
        self.pretrained_model.eval()
        
    def to_device(self, device: str) -> GPUCompatible:
        self.model = self.model.to(device)
        return self

    @property
    def name(self) -> str:
        return "OCRExtractor"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.STR],
                column_shapes=[(1)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["ocr_data"],
                column_types=[NdArrayType.STR],
                column_shapes=[(1)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            from PIL import Image

            data = row[0]
            input_img = Image.fromarray(data)            
            output = self.pretrained_model.inference(image=input_img, prompt=self.task_prompt)
            res=self.pretrained_model.json2token(output)
            sequence = re.sub(r"<.*?>", "", res)
            return sequence

        ret = pd.DataFrame()
        ret["ocr_data"] = df.apply(_forward, axis=1)
        return ret
