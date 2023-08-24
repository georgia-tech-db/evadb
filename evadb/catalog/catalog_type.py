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

from evadb.utils.generic_utils import EvaDBEnum


class Dimension(EvaDBEnum):
    ANYDIM  # noqa: F821


class TableType(EvaDBEnum):
    STRUCTURED_DATA  # noqa: F821
    VIDEO_DATA  # noqa: F821
    IMAGE_DATA  # noqa: F821
    DOCUMENT_DATA  # noqa: F821
    PDF_DATA  # noqa: F821

    # reserved for system generated tables
    # cannot be accessed/modified directly by user
    SYSTEM_STRUCTURED_DATA  # noqa: F821

    # Reserved for tables that are stored in native
    # database backend.
    NATIVE_DATA  # noqa: F821


class ColumnType(EvaDBEnum):
    BOOLEAN  # noqa: F821
    INTEGER  # noqa: F821
    FLOAT  # noqa: F821
    TEXT  # noqa: F821
    NDARRAY  # noqa: F821
    ANY  # noqa: F821


class NdArrayType(EvaDBEnum):
    INT8  # noqa: F821
    UINT8  # noqa: F821
    INT16  # noqa: F821
    INT32  # noqa: F821
    INT64  # noqa: F821
    UNICODE  # noqa: F821
    BOOL  # noqa: F821
    FLOAT32  # noqa: F821
    FLOAT64  # noqa: F821
    DECIMAL  # noqa: F821
    STR  # noqa: F821
    DATETIME  # noqa: F821
    ANYTYPE  # noqa: F821

    @classmethod
    def to_numpy_type(cls, t):
        from decimal import Decimal

        import numpy as np

        if t == cls.INT8:
            np_type = np.int8
        elif t == cls.UINT8:
            np_type = np.uint8
        elif t == cls.INT16:
            np_type = np.int16
        elif t == cls.INT32:
            np_type = np.int32
        elif t == cls.INT64:
            np_type = np.int64
        elif t == cls.UNICODE:
            np_type = np.unicode_
        elif t == cls.BOOL:
            np_type = np.bool_
        elif t == cls.FLOAT32:
            np_type = np.float32
        elif t == cls.FLOAT64:
            np_type = np.float64
        elif t == cls.DECIMAL:
            np_type = Decimal
        elif t == cls.STR:
            np_type = np.str_
        elif t == cls.DATETIME:
            np_type = np.datetime64
        elif t == cls.ANYTYPE:
            np_type = np.dtype(object)
        else:
            raise ValueError("Can not auto convert %s to numpy type" % t)

        return np_type


class VectorStoreType(EvaDBEnum):
    FAISS  # noqa: F821
    QDRANT  # noqa: F821


class VideoColumnName(EvaDBEnum):
    name  # noqa: F821
    id  # noqa: F821
    data  # noqa: F821
    seconds  # noqa: F821
    audio  # noqa: F821

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other

        if isinstance(other, EvaDBEnum):
            return self.value == other.value

        return False


class ImageColumnName(EvaDBEnum):
    name  # noqa: F821
    data  # noqa: F821


class DocumentColumnName(EvaDBEnum):
    name  # noqa: F821
    chunk_id  # noqa: F821
    data  # noqa: F821
    metadata  # noqa: F821


class PDFColumnName(EvaDBEnum):
    name  # noqa: F821
    page  # noqa: F821
    paragraph  # noqa: F821
    data  # noqa: F821
