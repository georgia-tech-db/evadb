
Optical Character Recognition UDF
=================================

This document is an overview of how a UDF consisting of a non-pytorch model can be integrated with Eva. Here, we take the example of the Optical Character Recognition UDF to understand the workflow to be followed for writing such a model.


Implementing the UDF
--------------------

EasyOCR, as the name suggests, is a Python package that allows computer vision developers to effortlessly perform Optical Character Recognition. The dependencies on the EasyOCR package are minimal, making it easy to configure your OCR development environment.

The EasyOCR package can be installed with a single pip command.

Once EasyOCR is installed, using a simple import statement it can be imported into your project.

As of this writing, EasyOCR can recognize text in 58 languages, including English, German, Hindi, Russian, and many more.

Inherited Classes
-----------------

The OCR UDF inherits two abtract classes namely 'AbstractClassifierUDF' and 'GPUCompatible'.

   * The `AbstractClassifierUDF` is a parent class that defines and implements standard methods for model inference for any given UDF. The `PytorchAbstractUDF`  also inherits this class. This class is defined in the abstract_udfs.py file. It consists of the following methods:

        * `__init__()` - This method defines and initializes variables that will be used throughout the UDF.


        * `name()` - An abstract method that returns the name of the UDF.


        * `labels()` - An abstract method that returns a list of labels required for the model's implementation. The index of the list is the value predicted by your model.


        * `classify()` - An abstract method that takes a batch of frames as input and returns the predictions by applying the classification model. The predictions are in the form of a DataFrame.
        


    * The `GPUCompatible` is a parent class that allows a model implemented by a given UDF to be assigned to a GPU device. It also stores the device information in a class variable which 
      can be accessed by other classes inheriting this class. This class is defined inside the gpu_compatible.py file.

        * `__init__()` - This method defines and initializes variables that will be used throughout the UDF.


        * `device_assignment()` - This method assigns the device passed by the UDF to the member variable of the class. Returns after enabling GPU for the device.


        * `to_device()` - An abtract method to enable GPU for the UDF's model being executed.


        You can however **choose to override** these methods depending on your requirements.


Methods in Optical Character Recognition UDF
--------------------------------------------

For executing optical character recogniton, the model being used is 'EasyOCR'. Hence an import statement is used to load the package for the UDF execution.
The following are the methods implemented by the Optical Character Recognition UDF:

        * `__init__()`- This method initializes the threshold value to be used for filtering the labels based on their confidence scores. Here, we also create an instance of the Reader class, by specifying the language for text extraction. If [‘en’] is passed as an attribute, the model will only detect the English text. If it finds text in other languages like Chinese or Japanese, those detections would be automatically ignored.


        * `name()` - This method returns the name of the Optical Character Recognition UDF.


        * `to_device()` - Here the reader instance is re-initialized by specifying the CPU/GPU device where the model is to be executed. Although this model is faster when executed on a GPU, if not specified, the model will be executed by default on the CPU.


        * `labels()` - This method is empty as there are no labels required for optical character recognition.


        * `classify()` - Accepts a dataframe of tensors as input. These tensor dataframes are converted to a numpy array before executing easyOcr. The function "readText()" is used for extracting the text predictions from a single frame or a batch of frames. The output of this method is a dataframe consisting of labels, bounding box coordinates as well as the confidence scores for each of the predictions.



Handling Batching v/s Non-batching
---------------------------------

EasyOCR can be used for detecting text from a single frame as well as from a batch of frames.

        * readtext() is used for extracting text from a single frame.


        * readtext_batched() is used for extracting text from a batch of frames.


Registering and Executing the UDF
---------------------------------

Now that you have implemented your UDF we need to register it into EVA and execute it. 

    1. Open an instance of the EVA client. 

        * You can do this either by running `python eva_cmd_client.py` or opening a notebook instance and use the `connect` method from `server.db_api`. 

    2. Now, we can register the OCR UDF with the following syntax:

            .. code-block:: sql
    
                CREATE UDF IF NOT EXISTS OpticalCharacterRecognition
                INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                        scores NDARRAY FLOAT32(ANYDIM))
                TYPE  Classification
                IMPL  'src/udfs/optical_character_recognition.py';    

        * Input is a frame of type NDARRAY with shape (3, ANYDIM, ANYDIM). 3 channels and any width or height. 
        * We return 3 variables for this UDF:
            * `labels`: The text labels extracted from each frame
            * `bboxes`: Rectangular coordinates of the bounding boxes. Unlike most pytorch UDFs, this UDF not just returns top left and bottom right coordinates of the detected text, but it returns all four coordinates of the rectangle.
            * `scores`: Confidence scores for the text prediction
        
        A status of 0 in the response denotes the successful registration of this UDF. 

    3. To make sure the UDF was successfully registered, you can open a mysql shell and run the below commands: 

        .. code-block:: sql

            mysql -u root; 
            use eva_catalog; 
            select * from udf;

        You should be able to see an entry for your UDF, if successfully registered.

    4. Now you can go ahead and execute your UDF on any video data like:

        .. code-block:: sql

            SELECT id, OpticalCharacterRecognition(data)) FROM MyVideo;
