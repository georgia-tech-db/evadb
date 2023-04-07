IO Descriptors
======================
EVA defines three main data types. The inputs and outputs from the UDFs must be of any of these types.

NumpyArray
------------
Used when the inputs or outputs of the UDF is of type Numpy Array. 

Parameters
------------ 
name (*str*): name of the numpy array. 

is_nullable (*bool*): boolean value indicating if the numpy array can the array be NULL.

type (*NdArrayType*): data type of elements in the numpy array. The available types can be found in eva/catalog/catalog_type.py in class NdArrayType

dimensions(*Tuple(int)*): shape of the numpy array

.. code-block:: python

    from eva.catalog.catalog_type import NdArrayType
    NumpyArray(
            name="input_arr",
            is_nullable=False,
            type=NdArrayType.INT32,
            dimensions=(2, 2),
    )



PyTorchTensor
--------------
name (*str*): name of the pytorch tensor.

is_nullable (*bool*): boolean value indicating if the pytorch tensor can the array be NULL.

type (*NdArrayType*): data type of elements in the pytorch tensor. The available types can be found in eva/catalog/catalog_type.py in class NdArrayType

dimensions(*Tuple(int)*): shape of the numpy array

.. code-block:: python

    from eva.catalog.catalog_type import NdArrayType
    PyTorchTensor(
                    name="input_arr",
                    is_nullable=False,
                    type=NdArrayType.INT32,
                    dimensions=(2, 2),
    )
    

PandasDataframe
----------------
columns (*List[str]*): list of strings that represent the expected column names in the pandas dataframe that is returned from the UDF.

column_types (*NdArrayType*): expected datatype of the column in the pandas dataframe returned from the UDF. The NdArrayType class is inherited from eva.catalog.catalog_type.

column_shapes (*List[tuples]*): list of tuples that represent the expected shapes of columns in the pandas dataframe returned from the UDF.

.. code-block:: python

    PandasDataframe(
                columns=["labels", "bboxes", "scores"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                ],
                column_shapes=[(None,), (None,), (None,)],
    )
