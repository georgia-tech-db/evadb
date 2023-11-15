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
from enum import Enum


class ErrorCode:
    def __init__(self, code, message=""):
        self.code = code
        self.default_message = message

    def __str__(self):
        return f"[{self.code}] {self.default_message}"

class ErrorManager:
    # Generic Error
    ERROR_GENERIC = ErrorCode(0, "")

    # Expected-Type Errors
    EXPECTED_SELECTION_STATEMENT = ErrorCode(100, "")
    EXPECTED_CREATE_TABLE_STATEMENT = ErrorCode(101, "")
    EXPECTED_SHOW_STATEMENT = ErrorCode(102, "")
    EXPECTED_INSERT_STATEMENT = ErrorCode(103, "")
    EXPECTED_EXPLAIN_STATEMENT = ErrorCode(104, "")
    EXPECTED_LOAD_STATEMENT = ErrorCode(105, "")
    EXPECTED_DROP_OBJECT_STATEMENT = ErrorCode(106, "")
    EXPECTED_RENAME_STATEMENT = ErrorCode(107, "")
    EXPECTED_CREATE_FUNCTION_STATEMENT = ErrorCode(108, "")
    EXPECTED_COLUMNS_NUMBER_MISMATCH = ErrorCode(109, "")
    QUERY_EXPECTS_ONE_CHILD = ErrorCode(110, "")
    EXPECTED_API_TOKEN_SET = ErrorCode(111, "")
    EXPECTED_PD_DF = ErrorCode(112, "")

    # Index Errors
    CANNOT_CREATE_INDEX_ON_MULIPLE_COLUMN = ErrorCode(1100, "")
    CREATE_INDEX_ONLY_ON_EXISTING_TABLE = ErrorCode(1101, "")
    CANNOT_CREATE_INDEX_ON_NONEXISTANT_COLUMN = ErrorCode(1102, "")
    INDEX_INPUT_TYPE_MISMATCH = ErrorCode(1103, "")
    INDEX_INPUT_DIM_MISMATCH = ErrorCode(1104, "")
    CREATE_INDEX_FIRST = ErrorCode(1105, "")

    # Type Errors
    UNSUPPORTED_TYPE = ErrorCode(2100, "")
    UNSUPPORTED_OPERATION = ErrorCode(2101, "")
    UNSUPPORTED_CLAUSE = ErrorCode(2102, "")
    UNSUPPORTED_LIBRARY = ErrorCode(2103, "")
    CONCURRENT_CALLS_NOT_SUPPORTED = ErrorCode(2104, "")

    # Not Found/Already Exists Errors
    TABLE_NOT_FOUND = ErrorCode(3100, "")
    TABLE_ALREADY_EXISTS = ErrorCode(3101, "")
    DIRECTORY_NOT_FOUND = ErrorCode(3102, "")
    DIRECTORY_ALREADY_EXISTS = ErrorCode(3103, "")
    FILE_NOT_FOUND = ErrorCode(3104, "")
    FILE_ALREADY_EXISTS = ErrorCode(3105, "")
    KEY_NOT_FOUND = ErrorCode(3106, "")

    # Failed-to Errors
    DROP_TABLE_FAILED = ErrorCode(4100, "")
    VECTOR_STORE_HANDLER_INITALIZATION_FAILED = ErrorCode(4101, "")
    RELATION_EXECUTE_FAILED = ErrorCode(4102, "")

    # Not implemented
    NOT_IMPLEMENTED = ErrorCode(9999, "")

    @staticmethod
    def get_error_message(error_code, additional_message=None):
        if additional_message:
            return f"{error_code} Details: {additional_message}"
        return str(error_code)