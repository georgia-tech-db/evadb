from typing import Optional

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe

class Dummy(AbstractFunction):
    @setup(cacheable=True, function_type='dummy', batchable=True)
    def setup(self, metric:Optional[str]=None):
        self.metric = metric
        self.count = 0

    @property
    def name(self) -> str:
        return "Dummy"

    @forward(
            input_signatures=[
                PandasDataframe(
                    columns=[
                        # "class",
                        # "predicted"
                    ],
                    # column_types=[NdArrayType.STR, NdArrayType.STR],
                    # column_shapes=[(None,), (None,)],
                )
            ],
            output_signatures=[
                PandasDataframe(
                    columns=["class", "predicted",],
                    column_types=[NdArrayType.STR, NdArrayType.STR, ],
                    column_shapes=[(None,), (None,), ]
                )
            ]
    )
    # TODO: allow columns=['*'] so that we can pass through all columns that were passed by users
    def forward(self, data: PandasDataframe) -> PandasDataframe:
        print('Running forward')
        print(data.columns)
        data['class'] = data['class'].astype(str) + ' ' + str(self.count)
        data['count'] = self.count
        self.count += 1 
        return data

    