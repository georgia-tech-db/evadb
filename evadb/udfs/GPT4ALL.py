# coding=utf-8
# Copyright 2018-2023 EVA
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

import os.path

import faiss

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
import numpy as np
import openai
import pandas as pd
import requests
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import GPT4All
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from sentence_transformers import SentenceTransformer

from evadb.catalog.catalog_type import NdArrayType
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.configuration.constants import EVA_DATABASE_DIR, EVA_ROOT_DIR
from evadb.udfs.abstract.abstract_udf import AbstractUDF
from evadb.udfs.decorators.decorators import forward, setup
from evadb.udfs.decorators.io_descriptors.data_types import PandasDataframe
from evadb.udfs.gpu_compatible import GPUCompatible


class GPT4AllQaUDF(AbstractUDF):
    @setup(cacheable=False, udf_type="FeatureExtraction", batchable=False)
    def setup(self):
        self.model_path = f"{EVA_ROOT_DIR}/data/models/ggml-gpt4all-j-v1.3-groovy.bin"
        check_file = os.path.isfile(self.model_path)
        if check_file == False:
            url = "https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin"
            r = requests.get(url, allow_redirects=True)
            open(self.model_path, "wb").write(r.content)

        openai.api_key = ConfigurationManager().get_value("third_party", "OPENAI_KEY")
        # If not found, try OS Environment Variable
        if len(openai.api_key) == 0:
            openai.api_key = os.environ.get("OPENAI_KEY", "")
        assert (
            len(openai.api_key) != 0
        ), "Please set your OpenAI API key in evadb.yml file (third_party, open_api_key) or environment variable (OPENAI_KEY)"

        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.llm = GPT4All(
            model=self.model_path,
            backend="gptj",
            callbacks=callback_manager,
            verbose=False,
        )

    @property
    def name(self) -> str:
        return "GPT4AllQaUDF"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data", "question"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(1), (1)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["answers"],
                column_types=[NdArrayType.STR],
                column_shapes=[(1)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            columns = row.axes[0]
            data = row.loc[columns[0]]
            question = row.loc[columns[1]]

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500, chunk_overlap=50
            )
            texts = text_splitter.split_text(data)

            # create vector index
            store = FAISS.from_texts(
                texts,
                HuggingFaceEmbeddings(),
                metadatas=[
                    {"source": f"Text chunk {i} of {len(texts)}"}
                    for i in range(len(texts))
                ],
            )
            faiss.write_index(store.index, "docs.faiss")

            qa = RetrievalQA.from_chain_type(
                llm=self.llm, chain_type="stuff", retriever=store.as_retriever()
            )
            ans = qa.run(question)
            return ans

        ret = pd.DataFrame()
        ret["answers"] = df.apply(_forward, axis=1)
        return ret
