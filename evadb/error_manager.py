from enum import Enum

class ErrorManager:
    class ErrorCode(Enum):
        # Generic Error
        ERROR_GENERIC = 0

        # Expected-Type Errors
        EXPECTED_SELECTION_STATEMENT = 100
        EXPECTED_CREATE_TABLE_STATEMENT = 101
        EXPECTED_SHOW_STATEMENT = 102
        EXPECTED_INSERT_STATEMENT = 103
        EXPECTED_EXPLAIN_STATEMENT = 104
        EXPECTED_LOAD_STATEMENT = 105
        EXPECTED_DROP_OBJECT_STATEMENT = 106
        EXPECTED_RENAME_STATEMENT = 107
        EXPECTED_CREATE_FUNCTION_STATEMENT = 108
        EXPECTED_COLUMNS_NUMBER_MISMATCH = 109
        QUERY_EXPECTS_ONE_CHILD = 110
        EXPECTED_API_TOKEN_SET = 111
        EXPECTED_PD_DF = 112

        # Index Errors
        CANNOT_CREATE_INDEX_ON_MULIPLE_COLUMN = 1100
        CREATE_INDEX_ONLY_ON_EXISTING_TABLE = 1101
        CANNOT_CREATE_INDEX_ON_NONEXISTANT_COLUMN = 1102
        INDEX_INPUT_TYPE_MISMATCH = 1103
        INDEX_INPUT_DIM_MISMATCH = 1104
        CREATE_INDEX_FIRST = 1105

        # Type Errors
        UNSUPPORTED_TYPE = 2100
        UNSUPPORTED_OPERATION = 2101
        UNSUPPORTED_CLAUSE = 2102
        UNSUPPORTED_LIBRARY = 2103
        CONCURRENT_CALLS_NOT_SUPPORTED = 2104

        # Not Found/Already Exists Errors
        TABLE_NOT_FOUND = 3100
        TABLE_ALREADY_EXISTS = 3101
        DIRECTORY_NOT_FOUND = 3102
        DIRECTORY_ALREADY_EXISTS = 3103
        FILE_NOT_FOUND = 3104
        FILE_ALREADY_EXISTS = 3105
        KEY_NOT_FOUND = 3106

        # Failed-to Errors
        DROP_TABLE_FAILED = 4100
        VECTOR_STORE_HANDLER_INITALIZATION_FAILED = 4101
        RELATION_EXECUTE_FAILED = 4102

        # Not implemented
        NOT_IMPLEMENTED = 9999

    @staticmethod
    def get_error_message(error_code, original_message):
        return f"[{error_code.name} - {error_code.value}] {original_message}"