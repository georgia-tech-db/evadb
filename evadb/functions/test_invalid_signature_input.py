import pandas as pd

from evadb.catalog.catalog_type import ColumnType, NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe

class InvalidSignatureInput(AbstractFunction):
    """
    Arguments:
        None

    Input Signatures:
        multiple input dataframes which is an invalid input signature
    """
    @property
    def name(self) -> str:
        return "InvalidSignature"
    
    @setup(cacheable=False)
    def setup(self) -> None:
        # Any setup or initialization can be done here if needed
        pass
    
    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["col1", "col2"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(None,), (None,)],
            ),
            PandasDataframe(
                columns=["col1", "col2"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["data1", "data2"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(None,), (None,)],
            )
        ],
    )
    def forward(self, input_df):
        # Create a DataFrame from the parsed data
        ans = []
        ans.append({'data1': 'data1', 'data2': 'data2'})
        output_dataframe = pd.DataFrame(ans, columns=['data1', 'data2'])

        return output_dataframe