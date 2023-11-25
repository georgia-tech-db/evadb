import numpy as np
import pandas as pd
import random
import string
from datetime import datetime, timedelta
from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.utils.generic_utils import try_to_import_cv2


class test_fn1(AbstractFunction):
    @setup(cacheable=False, function_type="cv2-transformation", batchable=True)
    def setup(self):
        try_to_import_cv2()

    @property
    def name(self):
        return "BlobDetector"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["string_col","int_col","float_col"],
                column_types=[NdArrayType.STR,NdArrayType.INT16,NdArrayType.FLOAT32],
                column_shapes=[(1,None),(None,None,3),(None,2,None)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["float_col","int_col"],
                column_types=[NdArrayType.FLOAT32,NdArrayType.INT32],
                column_shapes=[(2,None), (None, 3,3)],
            )
        ],
    )
    def forward(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        counting the blobs from a thresholded image

         Returns:
             ret (pd.DataFrame): The modified frame.
        """
        columns=['randcol1','randcol2']
                       
        column_types=[NdArrayType.FLOAT32,NdArrayType.INT32]
        column_shapes=[(2,None), (None, 3,3)]
        data = {}
        for col, ndtype, shape in zip(columns,column_types,column_shapes):
            random_data = generate_random_data(shape,ndtype)
            data[col] = [random_data]

        return pd.DataFrame(data)


def generate_random_data(dimensions, ndarray_type):
    """
    Generate random data based on the given dimensions and NdArrayType.

    :param dimensions: A tuple representing dimensions. 'None' is treated as 1.
    :param ndarray_type: The NdArrayType.
    :return: Randomly generated data.
    """

    # Replace 'None' with 1 in dimensions
    processed_dimensions = tuple(1 if d is None else d for d in dimensions)

    # Generate random data based on the NdArrayType
    if ndarray_type == "INT8":
        return np.random.randint(np.iinfo(np.int8).min, np.iinfo(np.int8).max, size=processed_dimensions, dtype=np.int8)
    elif ndarray_type == "UINT8":
        return np.random.randint(np.iinfo(np.uint8).min, np.iinfo(np.uint8).max, size=processed_dimensions, dtype=np.uint8)
    elif ndarray_type == "INT16":
        return np.random.randint(np.iinfo(np.int16).min, np.iinfo(np.int16).max, size=processed_dimensions, dtype=np.int16)
    elif ndarray_type == "INT32":
        return np.random.randint(np.iinfo(np.int32).min, np.iinfo(np.int32).max, size=processed_dimensions, dtype=np.int32)
    elif ndarray_type == "INT64":
        return np.random.randint(np.iinfo(np.int64).min, np.iinfo(np.int64).max, size=processed_dimensions, dtype=np.int64)
    elif ndarray_type == "FLOAT32":
        return np.random.rand(*processed_dimensions).astype(np.float32)
    elif ndarray_type == "FLOAT64":
        return np.random.rand(*processed_dimensions).astype(np.float64)
    elif ndarray_type == "UNICODE" or ndarray_type == "STR":
        return np.array([[''.join(random.choices(string.ascii_letters, k=10)) for _ in range(processed_dimensions[-1])] for _ in range(processed_dimensions[0])])
    elif ndarray_type == "BOOL":
        return np.random.choice([True, False], size=processed_dimensions)
    elif ndarray_type == "DATETIME":
        start_date = datetime.now()
        return np.array([start_date + timedelta(days=random.randint(0, 365)) for _ in range(np.prod(processed_dimensions))]).reshape(processed_dimensions)

    raise ValueError("Unsupported NdArrayType")