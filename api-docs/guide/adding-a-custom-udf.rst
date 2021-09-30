.. _guide-adding-a-custom-udf:

Adding a custom UDF 
===================

    This section is an overview of how you can create and execute a custom UDF. 

Introduction to UDFs
=====================

    * UDFs are user-defined functions, used to achieve a specific functionality on any video loaded to EVA. 
    * As the name suggests, these functions are defined and implemented by users. Once the UDFs are registered, you can 'call' these functions in your queries. 

Implementing your own UDF
=========================

    1. Create a new file under `src/udfs/` and give it a descriptive name. eg: `fastrcnn_object_detector.py`, `midas_depth_estimator.py`. 
    
    2. Here, you need to create and implement a class that derives from `PytorchAbstractUDF`.  

        * The `PytorchAbstractUDF` is a parent class that defines and implements standard methods for model inference.

        * `_get_predictions()` - an abstract method that needs to be implemented in your child class.

        * `classify()` - A  method that receives the frames and calls the `_get_predictions()` implemented in your child class. Based on GPU batch size, it also decides whether to split frames into chunks and performs the accumulation.

        * Additionally, it contains methods that help in:
            * Moving tensors to GPU
            * Converting tensors to numpy arrays. 
            * Defining the `forward()` function that gets called when the model is invoked. 
            * Basic transformations. 

        * You can however choose to override these methods depending on your requirements. 
        
    
    3.  A typical UDF class has the following components. 

        * `__init__()` constructor
            * Define all variables that will be required across all methods. 
            * Model loading happens here (can be a custom model you load with `torch.load()` or any of the existing models on torch hub etc.). Make sure you set it to `eval()`. 

        * `labels()` method
            * This should return a list of strings that your model aims to target. 
            * The index of the list is the value predicted by your model. 

        * `_get_predictions()` method
            * This is where all your model inference logic goes. 
            * While doing the computations, keep in mind that each call of this method is with a batch of frames. 

        * In case you have any other functional requirements (defining custom transformations etc.) you can choose to add more methods. Make sure each method you write is clear, concise and well-documented. 


Registering and executing the UDF
=================================

Now that you have implemented your UDF we need to register it into EVA and execute it. 

    1. Open an instance of the EVA client. 
        * You can do this either by running `python eva_cmd_client.py` or opening a notebook instance and use the `connect` method from `server.db_api`. 

    2. Now, we can register the UDF with the following syntax:

        `CREATE UDF [ IF NOT EXISTS ] <name> 
        INPUT  ( [ <arg_name> <arg_data_type> ] [ , ... ] )
        OUTPUT ( [ <result_name> <result_data_type> ] [ , ... ] )
        TYPE  <udf_type_name>
        IMPL  '<path_to_implementation>'`

        where,

            * **<name>** - specifies the unique identifier for the UDF.
            * **[ <arg_name> <arg_data_type> ] [ , ... ]** - specifies the name and data type of the udf input arguments. Name is kept for consistency (ignored by eva right now), arguments data type is required. ANYDIM means the shape is inferred at runtime.
            * **[ <result_name> <result_data_type> ] [ , ... ]** - specifies the name and data type of the udf output arguments. Users can access a specific output of the UDF similar to access a column of a table. Eg. <name>.<result_name>
            * **<udf_type_name>** - specifies the identifier for the type of the UDF. UDFs of the same type are assumed to be interchangeable. They should all have identical input and output arguments. For example, object classification can be one type.
            * **<path_to_implementation>** - specifies the path to the implementation class for the UDF


        A status of 0 denotes the successful registration of this UDF. 

    3. To make sure the UDF was successfully registered, you can open a mysql shell and run the below commands: 

        `mysql -u root; use eva_catalog; select * from udf;` 

        You should be able to see an entry for your UDF, if successfully registered.

    4. Now you can go ahead and execute your UDF on any video data like:

        `SELECT id, Unnest(FastRCNNObjectDetector(data)) FROM MyVideo`