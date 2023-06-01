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
import os
import faiss
import openai
import tempfile
import numpy as np
import pandas as pd

from moviepy.editor import *
from pytube import YouTube
from urllib.parse import urlparse, parse_qs

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe

from langchain.llms import GPT4All
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings


openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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" 


def transscribe_audio(file_path):
    file_size = os.path.getsize(file_path)
    file_size_in_mb = file_size / (1024 * 1024)
    if file_size_in_mb < 25:
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript
    else:
        print("Please provide a smaller audio file (max 25mb).")


class LangChainLLM(AbstractUDF):
    @setup(cacheable=False, udf_type="LangChain", batchable=False)
    def setup(self):
        url = "https://www.youtube.com/watch?v=H66-91nxLe4"

        # Extract the video ID from the url
        query = urlparse(url).query
        params = parse_qs(query)
        video_id = params["v"][0]

        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Download video audio
            yt = YouTube(url)

            # Get the first available audio stream and download this stream
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(output_path=temp_dir)

            # Convert the audio file to MP3
            audio_path = os.path.join(temp_dir, audio_stream.default_filename)
            audio_clip = AudioFileClip(audio_path)
            audio_clip.write_audiofile(os.path.join(temp_dir, f"{video_id}.mp3"))

            # Convert the audio file to MP3
            # Keep the path of the audio file
            audio_path = f"{temp_dir}/{video_id}.mp3"

            # Transscripe the MP3 audio to text
            transcript = transscribe_audio(audio_path)
            
            # Delete the original audio file
            os.remove(audio_path)
            
        textsplitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)
        texts = textsplitter.split_text(transcript.text)

        # Index construction
        store = FAISS.from_texts(
            texts, 
            # LlamaCppEmbeddings(model_path="./llama-embedding.bin"),
            HuggingFaceEmbeddings(),
            metadatas=[{"source": f"Text chunk {i} of {len(texts)}"} for i in range(len(texts))],
        )
        faiss.write_index(store.index, "docs.faiss")

        # Initialize LLM
        llm = GPT4All(model="./models/ggml-gpt4all-j.bin")
        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm, chain_type="stuff", retriever=store.as_retriever()
        )

    @property
    def name(self) -> str:
        return "LangChainLLM"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["question"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["response"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        def _forward(row: pd.Series) -> np.ndarray:
            question = row[0]
            print(question)
            return self.chain({"question": question}, return_only_outputs=True)

        ret = pd.DataFrame()
        ret["response"] = df.apply(_forward, axis=1)
        return ret
