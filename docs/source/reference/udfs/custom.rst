User-Defined Functions
======================

This section provides an overview of how you can create and use a custom user-defined function (UDF) in your queries. For example, you could write an UDF that wraps around your custom PyTorch model.

Part 1: Writing a custom UDF
------------------------------

During each step, use `this UDF implementation <https://github.com/georgia-tech-db/eva/blob/master/eva/udfs/yolo_object_detector.py>`_  as a reference.

1. Create a new file under `udfs/` folder and give it a descriptive name. eg: `yolo_object_detection.py`. 

  .. note::

      UDFs packaged along with EVA are located inside the `udfs <https://github.com/georgia-tech-db/eva/tree/master/eva/udfs>`_ folder.

2. Create a Python class that inherits from `PytorchClassifierAbstractUDF`.

* The `PytorchClassifierAbstractUDF` is a parent class that defines and implements standard methods for model inference.

* The functions setup and forward should be implemented in your child class. These functions can be implemented with the help of Decorators.

Setup
-----

An abstract method that must be implemented in your child class. The setup function can be used to initialize the parameters for executing the UDF. The parameters that need to be set are 

- cacheable: bool
 
  - True: Cache should be enabled. Cache will be automatically invalidated when the UDF changes.
  - False: cache should not be enabled.
- udf_type: str
  
  - object_detection: UDFs for object detection.
- batchable: bool
  
  - True: Batching should be enabled
  - False: Batching is disabled.

The custom setup operations for the UDF can be written inside the function in the child class. If there is no need for any custom logic, then you can just simply write "pass" in the function definition.

Example of a Setup function

.. code-block:: python

  @setup(cacheable=True, udf_type="object_detection", batchable=True)
  def setup(self, threshold=0.85):
      #custom setup function that is specific for the UDF
      self.threshold = threshold 
      self.model = torch.hub.load("ultralytics/yolov5", "yolov5s", verbose=False)

Forward
--------

An abstract method that must be implemented in your UDF. The forward function receives the frames and runs the deep learning model on the data. The logic for transforming the frames and running the models must be provided by you.
The arguments that need to be passed are

- input_signatures: List[IOColumnArgument] 
   
  Data types of the inputs to the forward function must be specified. If no constraints are given, then no validation is done for the inputs.

- output_signatures: List[IOColumnArgument]

  Data types of the outputs to the forward function must be specified. If no constraints are given, then no validation is done for the inputs.

A sample forward function is given below

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
        #the custom logic for the UDF
        outcome = []

        frames = torch.permute(frames, (0, 2, 3, 1))
        predictions = self.model([its.cpu().detach().numpy() * 255 for its in frames])
        
        for i in range(frames.shape[0]):
            single_result = predictions.pandas().xyxy[i]
            pred_class = single_result["name"].tolist()
            pred_score = single_result["confidence"].tolist()
            pred_boxes = single_result[["xmin", "ymin", "xmax", "ymax"]].apply(
                lambda x: list(x), axis=1
            )

            outcome.append(
                {"labels": pred_class, "bboxes": pred_boxes, "scores": pred_score}
            )

        return pd.DataFrame(outcome, columns=["labels", "bboxes", "scores"])

----------

Part 2: Registering and using the UDF in EVA Queries
------------------------------------------------------

Now that you have implemented your UDF, we need to register it as a UDF in EVA. You can then use the UDF in any query.

1. Register the UDF with a query that follows this template:

    `CREATE UDF [ IF NOT EXISTS ] <name>
    IMPL <path_to_implementation>;`

  where,

        * <name> - specifies the unique identifier for the UDF.
        * <path_to_implementation> - specifies the path to the implementation class for the UDF

  Here, is an example query that registers a UDF that wraps around the 'YoloObjectDetection' model that performs Object Detection.

  .. code-block:: sql

    CREATE UDF YoloDecorators
    IMPL  'eva/udfs/decorators/yolo_object_detection_decorators.py';
    

  A status of 0 in the response denotes the successful registration of this UDF.

2. Now you can execute your UDF on any video:

  .. code-block:: sql

      SELECT YoloDecorators(data) FROM MyVideo WHERE id < 5;

3. You can drop the UDF when you no longer need it.

  .. code-block:: sql

      DROP UDF IF EXISTS YoloDecorators;