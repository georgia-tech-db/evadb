from enum import IntEnum, unique


@unique
class StatementType(IntEnum):
    SELECT = 1,
    INSERT = 2,

    # add other types


class EvaStatement():
    """Base class for all the EvaStatement

    Attributes
    ----------
    stmt_type : StatementType
        the type of this statement - Select or Insert etc
    """

    def __init__(self, stmt_type: StatementType):
        self._stmt_type = stmt_type

    @property
    def stmt_type(self):
        return self._stmt_type


class EvaStatementList():
    """Holds the list of statements that we are processing

    Attributes
    ----------
    _eva_statement_list: list
        list of evaStatements

    """

    def __init__(self):
        self._eva_statement_list = []

    def add_statement(self, statement: EvaStatement):
        self._eva_statement_list.append(statement)

    def __len__(self) -> int:
        return len(self._eva_statement_list)

    def get_statement(self, idx: int) -> EvaStatement:
        if idx < len(self._eva_statement_list):
            return self._eva_statement_list[idx]
        else:
            return IndexError
