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

from evadb.utils.generic_utils import try_to_import_langchain

SUPPORTED_TYPES = [
    ".csv",
    ".doc",
    ".docx",
    ".enex",
    ".eml",
    ".epub",
    ".html",
    ".md",
    ".pdf",
    ".ppt",
    ".pptx",
    ".txt",
]


def _lazy_import_loader():
    try_to_import_langchain()
    from langchain.document_loaders import (
        CSVLoader,
        EverNoteLoader,
        PDFMinerLoader,
        TextLoader,
        UnstructuredEmailLoader,
        UnstructuredEPubLoader,
        UnstructuredHTMLLoader,
        UnstructuredMarkdownLoader,
        UnstructuredPowerPointLoader,
        UnstructuredWordDocumentLoader,
    )

    LOADER_MAPPING = {
        ".doc": (UnstructuredWordDocumentLoader, {}),
        ".docx": (UnstructuredWordDocumentLoader, {}),
        ".enex": (EverNoteLoader, {}),
        ".eml": (UnstructuredEmailLoader, {}),
        ".epub": (UnstructuredEPubLoader, {}),
        ".html": (UnstructuredHTMLLoader, {}),
        ".csv": (CSVLoader, {}),
        ".md": (UnstructuredMarkdownLoader, {}),
        ".pdf": (PDFMinerLoader, {}),
        ".ppt": (UnstructuredPowerPointLoader, {}),
        ".pptx": (UnstructuredPowerPointLoader, {}),
        ".txt": (TextLoader, {"encoding": "utf8"}),
        # Add more mappings for other file extensions and loaders as needed
    }
    return LOADER_MAPPING


def _lazy_import_text_splitter():
    try_to_import_langchain()
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    return RecursiveCharacterTextSplitter
