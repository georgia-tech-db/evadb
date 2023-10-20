.. _custom_ai_function:

Bring Your Own AI Function
==========================

This section provides an overview of how you can create and use a custom function in your queries. For example, you could write an function that wraps around your custom PyTorch model.

General Steps
--------------

Part 1: Writing a custom Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

During each step, use `this function implementation <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/yolo_object_detector.py>`_  as a reference.

1. Create a new file under `functions/` folder and give it a descriptive name. eg: `yolo_object_detection.py`. 

  .. note::

      Functions packaged along with EvaDB are located inside the `functions <https://github.com/georgia-tech-db/evadb/tree/master/evadb/functions>`_ folder.

2. Create a Python class that inherits from `AbstractFunction`.

* The `AbstractFunction` is a parent class that defines and implements standard methods for model inference.

* The functions setup and forward should be implemented in your child class. These functions can be implemented with the help of Decorators.

**Setup**

The abstract method `setup` must be implemented in your function. The setup function can be used to initialize the parameters for executing the function. The parameters that need to be set are 

- cacheable: bool
 
  - True: Cache should be enabled. Cache will be automatically invalidated when the function changes.
  - False: cache should not be enabled.
- function_type: str
  
  - object_detection: functions for object detection.
- batchable: bool
  
  - True: Batching should be enabled
  - False: Batching is disabled.

Any additional arguments needed for creating the function must be passed as arguments to the setup function. (Please refer to the 
`ChatGPT <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/chatgpt.py>`__ function example).

The additional arguments are passed with the CREATE command. Please refer to `CREATE <https://evadb.readthedocs.io/en/stable/source/reference/evaql/create_function.html>`_ command documentation.

The custom setup operations for the function can be written inside the function in the child class. If there is no need for any custom logic, then you can just simply write "pass" in the function definition.


**Forward**

The abstract method `forward` must be implemented in your function. The forward function receives the frames and runs the deep learning model on the data. The logic for transforming the frames and running the models must be provided by you. Using the forward decorator is optional.

The arguments that need to be passed are

- input_signatures: List[IOArgument]
   
  Data types of the inputs to the forward function must be specified. If no constraints are given, then no validation is done for the inputs.

- output_signatures: List[IOArgument]

  Data types of the outputs to the forward function must be specified. If no constraints are given, then no validation is done for the inputs.

A list of IO types in EvaDB are found in `IODescriptors <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/decorators/io_descriptors/data_types.py>`_ folder.

Please ensure that the names of the columns in the dataframe match the names specified in the decorators.


Part 2: Registering and using the function in EvaDB Queries
-----------------------------------------------------------

Now that you have implemented your function, we need to register it as a function in EvaDB. You can then use the function in any query.

1. Register the function with a query that follows this template:

  .. code-block:: sql

    CREATE FUNCTION [ IF NOT EXISTS ] <name>
    IMPL <path_to_implementation>;


where,

* <name> - specifies the unique identifier for the function.
* <path_to_implementation> - specifies the path to the implementation class for the function


2. Execute your function on any data:

  .. code-block:: sql

      SELECT <name>(data) FROM table [condition];

3. You can drop the function when you no longer need it.

  .. code-block:: sql

      DROP FUNCTION IF EXISTS <name>;

----------

Examples
---------

1. Yolo Object Detection
^^^^^^^^^^^^^^^^^^^^^^^^^

The following code can be used to create an Object Detection function using Yolo

1. Inherit from the `Abstract Function` class. It is a parent class that defines and implements standard methods for model inference.

    .. code-block:: python
  
        class Yolo(AbstractFunction)

2. Create the setup function. Here we set the parameters batchable as True, cacheable as True and function type as 'object_detection'. The function has code to perform some basic initialization for the Yolo function. 

    .. code-block:: python

      @setup(cacheable=True, function_type="object_detection", batchable=True)
      def setup(self, model: str, threshold=0.3):
         try_to_import_ultralytics() #function to try and import the YOLO library.
         from ultralytics import YOLO
    
          self.threshold = threshold #sets the threshold for the model
          self.model = YOLO(model) #initializes the model
          self.device = "cpu" #sets the device as CPU

3. Create the forward function.  The logic for transforming the frames and running the models must be provided here. 

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

**Ensure that the column names of the dataframe matches those given in the decorator.**

4. Register the function

      .. code-block:: sql

        CREATE FUNCTION Yolo
        IMPL  'evadb/functions/yolo_object_detector.py';

5. Execute the function

      .. code-block:: sql

        SELECT Yolo(data) FROM MyVideo WHERE id < 5;

6. Drop the function

      .. code-block:: sql

        DROP FUNCTION IF EXISTS Yolo;

----------

2. ChatGPT function
^^^^^^^^^^^^^^^^^^^^^^^^^

1. Inherit from AbstractFunction class.

    .. code-block:: python

      # this function takes the model and temperature as arguments from the user.

      @setup(cacheable=True, function_type="chat-completion", batchable=True)
      def setup( self, model="gpt-3.5-turbo", temperature: float = 0,) -> None:
          assert model in _VALID_CHAT_COMPLETION_MODEL, f"Unsupported ChatGPT {model}"
          self.model = model
          self.temperature = temperature


2. Implement the forward function

    .. code-block:: python

      @forward(
          input_signatures=[
              PandasDataframe(
                  columns=["query", "content", "prompt"],
                  column_types=[
                      NdArrayType.STR,
                      NdArrayType.STR,
                      NdArrayType.STR,
                  ],
                  column_shapes=[(1,), (1,), (None,)],
              )
          ],
          output_signatures=[
              PandasDataframe(
                  columns=["response"],
                  column_types=[
                      NdArrayType.STR,
                  ],
                  column_shapes=[(1,)],
              )
          ],
      )
      def forward(self, text_df):
        #importing openai
        try_to_import_openai()
        import openai

        #getting the data
        content = text_df[text_df.columns[0]]
        responses = []

        for prompt in content:
          response = openai.ChatCompletion.create(model="gpt-3.5-turbo", \
                                                  temperature=0.2, \
                                                  messages=[{"role": "user", "content": prompt}])
          response_text = response.choices[0].message.content
          responses.append(response_text)
        
        return_df = pd.DataFrame({"response": responses})


(Please refer to `ChatGPT <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/chatgpt.py>`__ function for exact implementation in EvaDB.)

3. Register the function

    .. code-block:: sql

      CREATE FUNCTION OpenAICompletion
      IMPL  'evadb/functions/chatgpt.py'
      model gpt-4-0314 ;

4. Execute the function

    .. code-block:: sql

      SELECT OpenAICompletion('summarize', content) FROM MyTextCSV;

5. Drop the function

    .. code-block:: sql
  
      DROP FUNCTION IF EXISTS OpenAICompletion;
    



    


      


  

  
