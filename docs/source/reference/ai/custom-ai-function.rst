.. _custom_ai_function:

Bring Your Own AI Function
==========================

This section provides an overview of how you can create and use a custom function in your queries. For example, you could write an function that wraps around your custom PyTorch model.

Part 1: Writing a custom Function
---------------------------------

During each step, use `this function implementation <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/yolo_object_detector.py>`_  as a reference.

1. Create a new file under `functions/` folder and give it a descriptive name. eg: `yolo_object_detection.py`. 

  .. note::

      Functions packaged along with EvaDB are located inside the `functions <https://github.com/georgia-tech-db/evadb/tree/master/evadb/functions>`_ folder.

2. Create a Python class that inherits from `AbstractFunction`.

* The `AbstractFunction` is a parent class that defines and implements standard methods for model inference.

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
     try_to_import_ultralytics() #function to try and import the YOLO library.
     from ultralytics import YOLO

      self.threshold = threshold #sets the threshold for the model
      self.model = YOLO(model) #initializes the model
      self.device = "cpu" #sets the device as CPU

Forward
--------

The abstract method `forward` must be implemented in your function. The forward function receives the frames and runs the deep learning model on the data. The logic for transforming the frames and running the models must be provided by you.
The arguments that need to be passed are

- input_signatures: List[IOArgument]
   
  Data types of the inputs to the forward function must be specified. If no constraints are given, then no validation is done for the inputs.

- output_signatures: List[IOArgument]

  Data types of the outputs to the forward function must be specified. If no constraints are given, then no validation is done for the inputs.

A list of IO types in EvaDB are found in `IODescriptors <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/decorators/io_descriptors/data_types.py>`_ folder.

A sample forward function is given below

.. code-block:: python
    # input is a pandas dataframe which has 1 column named data that is of type FLOAT32. The column shape is (None, None, 3)
    # output is a pandas dataframe with 3 columns. The column names are labels, bboxes and scores.  
    # The column shapes are (None,), (None,) and (None,)
    @forward(
          input_signatures=[
              PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
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
        
        frames = np.ravel(frames.to_numpy())
        list_of_numpy_images = [its for its in frames]
        predictions = self.model.predict(
            list_of_numpy_images, device=self.device, conf=self.threshold, verbose=False
        )
        for pred in predictions:
            single_result = pred.boxes
            pred_class = [self.model.names[i] for i in single_result.cls.tolist()]
            pred_score = single_result.conf.tolist()
            pred_score = [round(conf, 2) for conf in single_result.conf.tolist()]
            pred_boxes = single_result.xyxy.tolist()
            sorted_list = list(map(lambda i: i < self.threshold, pred_score))
            t = sorted_list.index(True) if True in sorted_list else len(sorted_list)
            outcome.append(
                {
                    "labels": pred_class[:t],
                    "bboxes": pred_boxes[:t],
                    "scores": pred_score[:t],
                },
            )
        return pd.DataFrame(
            outcome,
            columns=[
                "labels",
                "bboxes",
                "scores",
            ],
        )


Please ensure that the names of the columns in the dataframe match the names specified in the decorators.

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

    CREATE FUNCTION Yolo
    IMPL  'evadb/functions/yolo_object_detector.py';
    


2. Now you can execute your function on any video:

  .. code-block:: sql

      SELECT Yolo(data) FROM MyVideo WHERE id < 5;

3. You can drop the function when you no longer need it.

  .. code-block:: sql

      DROP FUNCTION IF EXISTS Yolo;
