from enum import unique, IntEnum


@unique
class PlanNodeType(IntEnum):
    SEQUENTIAL_SCAN_TYPE = 1
    STORAGE_PLAN = 2
    PP_FILTER_TYPE = 3
    SEQSCAN = 4
    LOGICAL_PROJECTION = 5
    LOGICAL_INNER_JOIN = 6
    TABLE = 7
