import numpy as np

from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType, \
    ExpressionReturnType
import statistics
from src.models.storage.batch import FrameBatch

class AggregationExpression(AbstractExpression):
    def __init__(self, exp_type: ExpressionType, left: AbstractExpression,
                 right: AbstractExpression):
        children = []
        if left is not None:
            children.append(left)
        if right is not None:
            children.append(right)
        super().__init__(exp_type, rtype=ExpressionReturnType.INTEGER, ## can also be a float
                         children=children)

    def evaluate(self,  batch: FrameBatch):
        args = [frame._data for frame in batch._frames]
        values = self.get_child(0).evaluate(args)
        
        if self.etype == ExpressionType.AGGREGATION_SUM:
            return sum(sum(values))
        elif self.etype == ExpressionType.AGGREGATION_COUNT:
            return len(values)
        elif self.etype == ExpressionType.AGGREGATION_AVG:
            return np.array(values).mean()
        elif self.etype == ExpressionType.AGGREGATION_MIN:
            return min(values)
        elif self.etype == ExpressionType.AGGREGATION_MAX:
            return max(values)
