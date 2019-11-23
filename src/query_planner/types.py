from enum import unique, IntEnum


@unique
class PlanNodeType(IntEnum):
    SEQUENTIAL_SCAN_TYPE = 1
    STORAGE_PLAN = 2
    PP_FILTER_TYPE = 3
    # add other types