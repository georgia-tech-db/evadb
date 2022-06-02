from typing import List
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch


def apply_project(batch: Batch, project_list: List[AbstractExpression]):
    if not batch.empty() and project_list:
        batches = [expr.evaluate(batch) for expr in project_list]
        batch = Batch.merge_column_wise(batches)
    return batch


def apply_predicate(batch: Batch, predicate: AbstractExpression):
    if not batch.empty() and predicate is not None:
        outcomes = predicate.evaluate(batch).frames
        batch = Batch(
            batch.frames[(outcomes > 0).to_numpy()].reset_index(drop=True))
    return batch
