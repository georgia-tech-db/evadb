User-Defined Functions
======================

This section provides an overview of how you can create and use a custom user-defined function (UDF) in your queries. For example, you could write a UDF that wraps around a PyTorch model.


Part 1: Writing a Custom UDF
------------------------------

During each step, use the `UDF implementation <https://github.com/georgia-tech-db/eva/blob/master/eva/udfs/fastrcnn_object_detector.py>`_ as a reference.

1. Create a new file under `udfs/` folder and give it a descriptive name, e.g., `fastrcnn_object_detector.py`.

   .. note::

      UDFs packaged along with EVA are located inside the `udfs <https://github.com/georgia-tech-db/eva/tree/master/eva/udfs>`_ folder.

2. Create a Python class that inherits from `PytorchClassifierAbstractUDF`.

   - The ``PytorchClassifierAbstractUDF`` is a parent class that defines and implements standard methods for model inference.
   - Implement the ``setup`` and ``forward`` functions in your child class. These functions can be implemented with the help of decorators.

Setup
-----

An abstract method that must be implemented in your child class. The `setup` function can be used to initialize the parameters for executing the UDF. The following parameters must be set:

- ``cacheable``: bool

  - `True`: Cache should be enabled. The cache will be automatically invalidated when the UDF changes.
  - `False`: Cache should not be enabled.

- ``udf_type``: str

  - `object_detection`: UDFs for object detection.

- ``batchable``: bool

  - `True`: Batching should be enabled.
  - `False`: Batching is disabled.

The custom setup operations for the UDF can be written inside the function in the child class. If no custom logic is required, then you can just write `pass` in the function definition.

Example of the `setup` function:

.. code-block:: python

    @setup(cacheable=True, udf_type="object_detection", batchable=True)
    def setup(self, threshold=0.85):
        self.threshold = threshold
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            weights="COCO_V1", progress=False
        )
        self.model.eval()

In this instance, we have configured the `cacheable` and `batchable` attributes to `True`. As a result, EVA will cache the UDF outputs and utilize batch processing for increased efficiency.

Forward
--------

An abstract method that must be implemented in your child class. The `forward` function receives the frames and runs the Deep Learning model on the frames. The logic for transforming the frames and running the models must be provided by you. The arguments that need to be passed are:

- ``input_signatures``: List[IOColumnArgument]

  Data types of the inputs to the `forward` function must be specified. If no constraints are given, no validation is done for the inputs.

- ``output_signatures``: List[IOColumnArgument]

  Data types of the outputs from the `forward` function must be specified. If no constraints are given, no validation is done for the inputs.

A sample ``forward`` function is given below:

.. code-block:: python
    
    @forward(
        input_signatures=[
            PyTorchTensor(
                name="input_col",
                is_nullable=False,
                type=NdArrayType.FLOAT32,
                dimensions=(1, 3, 540, 960),
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["labels", "bboxes", "scores"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.FLOAT32,
                    NdArrayType.FLOAT32,
                ],
                column_shapes=[(None,), (None,), (None,)],
            )
        ],
    )
    def forward(self, frames: Tensor) -> pd.DataFrame:
        predictions = self.model(frames)
        outcome = []
        for prediction in predictions:
            pred_class = [
                str(self.labels[i]) for i in list(self.as_numpy(prediction["labels"]))
            ]
            pred_boxes = [
                [i[0], i[1], i[2], i[3]]
                for i in list(self.as_numpy(prediction["boxes"]))
            ]

In this instance, the forward function takes a PyTorch tensor of Float32 type with a shape of (1, 3, 540, 960) as input. The resulting output is a pandas dataframe with 3 columns, namely "labels", "bboxes", and "scores", and of string, float32, and float32 types respectively.


Part 2: Registering and using the UDF in queries
------------------------------------------------------

Now that you have implemented your UDF we need to register it in EVA. You can then use the function in any query.

Register the UDF in EVA
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

  CREATE UDF [ IF NOT EXISTS ] <name>
  IMPL <implementation_path>;


``name`` - specifies the unique identifier for the UDF.

``implementation_path`` - specifies the path to the implementation class for the UDF

Here, is an example query that registers a UDF that wraps around the ``fasterrcnn_resnet50_fpn`` model that performs Object Detection.

.. code-block:: sql

  CREATE UDF FastRCNNObjectDetector
  IMPL  'eva/udfs/fastrcnn_object_detector.py';
    


Call registered UDF in a query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

  SELECT FastRCNNObjectDetector(data) FROM MyVideo WHERE id < 5;

Drop the UDF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

  DROP UDF IF EXISTS FastRCNNObjectDetector;