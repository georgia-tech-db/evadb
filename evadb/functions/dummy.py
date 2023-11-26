from typing import Optional

from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe, PandasColumn, NewPandasDataFrame

class Dummy(AbstractFunction):
    @setup(cacheable=False, function_type='dummy', batchable=True)
    def setup(self, metric:Optional[str]=None):
        self.metric = metric
        self.count = 0

    @property
    def name(self) -> str:
        return "Dummy"

    @forward(
        input_signatures=[
            NewPandasDataFrame(
                columns=[
                    PandasColumn('race', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                    PandasColumn('age', type=NdArrayType.INT16, shape=(None,), is_nullable=False),
                    PandasColumn('sex', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                    PandasColumn('charge', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                    PandasColumn('n_prior', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                    PandasColumn('stay', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                    PandasColumn('huh', type=NdArrayType.STR, shape=(None,), is_nullable=False),

                    # Should let users know that this column was not found
                    # PandasColumn('non-extant_col', type=NdArrayType.ANYTYPE, shape=(None,), is_nullable=False, required=False),
                    # PandasColumn('class', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                    # PandasColumn('predicted', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                ]
            )
        ],
        output_signatures=[
            NewPandasDataFrame(
                columns=[
                    PandasColumn('class', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                    PandasColumn('predicted', type=NdArrayType.STR, shape=(None,), is_nullable=False),
                ]
            )
        ]
    )
    def forward(self, data: PandasDataframe) -> PandasDataframe:
        return data