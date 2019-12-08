from .abstract_expression import AbstractExpression, ExpressionType, \
    ExpressionReturnType

import numpy as np


class TupleValueExpression(AbstractExpression):
    def __init__(self, col_idx: int = None, col_name: str = None):
        # setting return type to be invalid not sure if that is correct
        # no child so that is okay
        super().__init__(ExpressionType.TUPLE_VALUE,
                         rtype=ExpressionReturnType.INVALID)
        self._col_name = col_name
        # todo
        self._table_name = None
        self._col_idx = col_idx

    # def evaluate(AbstractTuple tuple1, AbstractTuple tuple2):

    # don't know why are we getting 2 tuples
    # comments added to abstract class,
    # maybe we should move to *args

    # assuming tuple1 to be valid

    # remove this once doen with tuple class
    def evaluate(self, *args):
        tuple1 = None
        if args is None:
            # error Handling
            pass
        frames = args
        
        frames_np = [np.array(tuple1)[:,  self._col_idx] for tuple1 in frames]
        return frames_np[0]

    # ToDo
    # implement other boilerplate functionality
