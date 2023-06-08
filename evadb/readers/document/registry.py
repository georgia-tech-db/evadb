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


def _lazy_import_loader():
    import_err_msg = "`langchain` package not found, please run `pip install langchain`"
    try:
        from langchain.document_loaders import (
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
    except ImportError:
        raise ImportError(import_err_msg)

    LOADER_MAPPING = {
        ".doc": (UnstructuredWordDocumentLoader, {}),
        ".docx": (UnstructuredWordDocumentLoader, {}),
        ".enex": (EverNoteLoader, {}),
        ".eml": (UnstructuredEmailLoader, {}),
        ".epub": (UnstructuredEPubLoader, {}),
        ".html": (UnstructuredHTMLLoader, {}),
        ".md": (UnstructuredMarkdownLoader, {}),
        ".pdf": (PDFMinerLoader, {}),
        ".ppt": (UnstructuredPowerPointLoader, {}),
        ".pptx": (UnstructuredPowerPointLoader, {}),
        ".txt": (TextLoader, {"encoding": "utf8"}),
        # Add more mappings for other file extensions and loaders as needed
    }
    return LOADER_MAPPING


SUPPORTED_TYPES = [
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
