from src.query_parser.types import StatementType


class EvaStatement:
    """
    Base class for all the EvaStatement

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
