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
    try_to_import_torchvision,
    try_to_import_transformers,
)

# import cv2


class OCRExtractor(AbstractUDF, GPUCompatible):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        try_to_import_torch()
        try_to_import_torchvision()
        try_to_import_transformers()
        from transformers import DonutProcessor, VisionEncoderDecoderModel

        self.processor = DonutProcessor.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-cord-v2"
        )
        self.model = VisionEncoderDecoderModel.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-cord-v2"
        )
        # prepare decoder inputs
        task_prompt = "<s_cord-v2>"
        self.decoder_input_ids = self.processor.tokenizer(
            task_prompt, add_special_tokens=False, return_tensors="pt"
        ).input_ids

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
            data = row[0]
            import torch
            import torchvision

            # image = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
            image = torchvision.transforms.ToPILImage()(data)
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            device = "cuda" if torch.cuda.is_available() else "cpu"
            outputs = self.model.generate(
                pixel_values.to(device),
                decoder_input_ids=self.decoder_input_ids.to(device),
                max_length=self.model.decoder.config.max_position_embeddings,
                early_stopping=True,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
                output_scores=True,
            )
            sequence = self.processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(
                self.processor.tokenizer.pad_token, ""
            )
            sequence = re.sub(r"<.*?>", "", sequence)
            return sequence

        ret = pd.DataFrame()
        ret["ocr_data"] = df.apply(_forward, axis=1)
        return ret
