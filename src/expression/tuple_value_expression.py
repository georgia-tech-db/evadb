from .abstract_expression import AbstractExpression, ExpressionType, \
    ExpressionReturnType


class TupleValueExpression(AbstractExpression):
    def __init__(self, col_idx: int):
        # setting return type to be invalid not sure if that is correct
        # no child so that is okay
        super().__init__(ExpressionType.TUPLE_VALUE,
                         rtype=ExpressionReturnType.INVALID)
        self._col_idx = col_idx
        # todo
        self._table_name = None
        self._col_name = None

    # def evaluate(AbstractTuple tuple1, AbstractTuple tuple2):

    # don't know why are we getting 2 tuples
    # comments added to abstract class,
    # maybe we should move to *args

    # assuming tuple1 to be valid

    # remove this once doen with tuple class
    def evaluate(self, *args):
        if args == None:
            # error Handling
            pass
        tuple1 = args[0]
        return tuple1[(self._col_idx)]

    # ToDo
    # implement other boilerplate functionality
