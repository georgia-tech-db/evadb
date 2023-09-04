.. _udf:

Functions
======================

This section provides an overview of how you can create and use a custom function in your queries. For example, you could write an function that wraps around your custom PyTorch model.

Part 1: Writing a custom Function
---------------------------------

During each step, use `this function implementation <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/yolo_object_detector.py>`_  as a reference.

1. Create a new file under `functions/` folder and give it a descriptive name. eg: `yolo_object_detection.py`. 

  .. note::

      Functions packaged along with EvaDB are located inside the `functions <https://github.com/georgia-tech-db/evadb/tree/master/evadb/functions>`_ folder.

2. Create a Python class that inherits from `PytorchClassifierAbstractFunction`.

* The `PytorchClassifierAbstractFunction` is a parent class that defines and implements standard methods for model inference.

* The functions setup and forward should be implemented in your child class. These functions can be implemented with the help of Decorators.

Setup
-----

An abstract method that must be implemented in your child class. The setup function can be used to initialize the parameters for executing the function. The parameters that need to be set are 

- cacheable: bool
 
  - True: Cache should be enabled. Cache will be automatically invalidated when the function changes.
  - False: cache should not be enabled.
- function_type: str
  
  - object_detection: functions for object detection.
- batchable: bool
  
  - True: Batching should be enabled
  - False: Batching is disabled.

The custom setup operations for the function can be written inside the function in the child class. If there is no need for any custom logic, then you can just simply write "pass" in the function definition.

Example of a Setup Function

.. code-block:: python

  @setup(cacheable=True, function_type="object_detection", batchable=True)
  def setup(self, threshold=0.85):
      #custom setup function that is specific for the function
      self.threshold = threshold 
      self.model = torch.hub.load("ultralytics/yolov5", "yolov5s", verbose=False)

Forward
--------

An abstract method that must be implemented in your function. The forward function receives the frames and runs the deep learning model on the data. The logic for transforming the frames and running the models must be provided by you.
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
        #the custom logic for the function
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

Part 2: Registering and using the function in EvaDB Queries
-----------------------------------------------------------

Now that you have implemented your function, we need to register it as a function in EvaDB. You can then use the function in any query.

1. Register the function with a query that follows this template:

    `CREATE FUNCTION [ IF NOT EXISTS ] <name>
    IMPL <path_to_implementation>;`

  where,

        * <name> - specifies the unique identifier for the function.
        * <path_to_implementation> - specifies the path to the implementation class for the function

  Here, is an example query that registers a function that wraps around the 'YoloObjectDetection' model that performs Object Detection.

  .. code-block:: sql

    CREATE FUNCTION YoloDecorators
    IMPL  'evadb/functions/decorators/yolo_object_detection_decorators.py';
    

  A status of 0 in the response denotes the successful registration of this function.

2. Now you can execute your function on any video:

  .. code-block:: sql

      SELECT YoloDecorators(data) FROM MyVideo WHERE id < 5;

3. You can drop the function when you no longer need it.

  .. code-block:: sql

      DROP FUNCTION IF EXISTS YoloDecorators;
