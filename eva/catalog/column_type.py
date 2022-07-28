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
from enum import Enum, IntEnum, auto


class Dimension(IntEnum):
    ANYDIM = -1


class ColumnType(Enum):
    BOOLEAN = 1
    INTEGER = 2
    FLOAT = 3
    TEXT = 4
    NDARRAY = 5
    ANY = 6


class NdArrayType(Enum):
    INT8 = auto()
    UINT8 = auto()
    INT16 = auto()
    INT32 = auto()
    INT64 = auto()
    UNICODE = auto()
    BOOL = auto()
    FLOAT32 = auto()
    FLOAT64 = auto()
    DECIMAL = auto()
    STR = auto()
    DATETIME = auto()
    ANYTYPE = auto()

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
