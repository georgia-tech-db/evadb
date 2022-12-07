# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Iterator
import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import apply_predicate
from eva.models.storage.batch import Batch
from eva.planner.predicate_plan import PredicatePlan
from eva.expression.expression_utils import find_LIKE_in_exp_tree, convert_id_list_to_expression


class PredicateExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: PredicatePlan):
        super().__init__(node)
        self.predicate = node.predicate
        self.table_ref = node.table_ref

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]

        # We are going to treat LIKE as a special kind of predicate.
        # It needs to be executed before any other predicate.
        like_exp = find_LIKE_in_exp_tree(self.predicate)
        if like_exp is not None:
            if not self.table_ref.is_table_atom:
                raise NotImplementedError("LIKE expressions on non-atomic tables are not supported.")
            like_exp.table_info = self.table_ref.table
            
            # query has only one predicate and it is `LIKE`
            # bypass the standard predicate routine and preserve the similarity order
            if like_exp is self.predicate:
                like_exp.compute_similar_idx()
                # IDs of similar images
                similar_idx = like_exp.similar_idx
                '''
                The next line is doing: given an id list, which is the ids we want to select,
                for example: [8, 2, 4, 7]
                convert it to predicate:
                id==8 OR (id==2 OR (id==4 OR id==7))

                The reason for doing this is that we want to push down the id(index) of
                images we need to the storage executor, so that it will not read all the images.

                This is a kind of optimization that already exists in eva.
                To follow the eva conventions, we need to convert this series of ids to predicate
                '''
                id_eq_expr = convert_id_list_to_expression(similar_idx, self.table_ref.table.table_name)

                # child_output = child_executor.exec(*args, **kwargs)
                child_output = child_executor.exec(*args, **kwargs, predicate=id_eq_expr)
                child_output = list(child_output)
                child_output = Batch.concat(child_output, copy=False)
                # now we have the tuples containing similar images
                output_frames = child_output.frames
                
                id_col_name = self.table_ref.table.table_name + ".id"
                output = []
                # restore the order given by similar_idx
                for idx in similar_idx:
                    row = output_frames.loc[output_frames[id_col_name] == idx]
                    output.append(row)

                # yield Batch(child_output.frames.iloc[similar_idx])
                yield Batch(pd.concat(output, ignore_index=True))
                return

        for batch in child_executor.exec(*args, **kwargs):
            batch = apply_predicate(batch, self.predicate)
            if not batch.empty():
                yield batch
