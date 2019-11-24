from enum import IntEnum, unique


@unique
class StatementType(IntEnum):
    """
    Manages enums for all the sql-like statements supported
    """
    SELECT = 1,

    # add other types
