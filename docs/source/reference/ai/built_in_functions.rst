Built-In Functions
==========

.. _built-in-functions:


MnistImageClassifier
Defined in: evadb/functions/mnist_image_classifier.py
.. code:: mysql
   MnistImageClassifier(input).label
Recognizes and classifies images of handwritten numbers.


FastRCNNObjectDetector
Defined in: evadb/functions/fastrcnn_object_detector.py
.. code:: mysql
   FastRCNNObjectDetector(frame).labels
Recognizes and classifies objects.


ArrayCount
Defined in: evadb/functions/ndarray/array_count.py
.. code:: mysql
   ArrayCount(input_frame, search_key)
Returns the number of times that given search key was found in the input frame.


Crop
Defined in: evadb/functions/ndarray/crop.py
.. code:: mysql
   Crop(data, bbox)
Crops input frames based upon the bounding box coordinates and returns the cropped version.


Open
Defined in: evadb/functions/ndarray/open.py
.. code:: mysql
   Open(image_path)
Opens and caches an image. Returns a data frame containing the image.


Similarity
Defined in: evadb/functions/ndarray/similarity.py
.. code:: mysql
   Similarity(frame1, frame2)
Returns similarity score between two feature vectors.


ChatGPT
Defined in: evadb/functions/chatgpt.py
.. code:: mysql
   ChatGPT(query, text)
Passes the query and relevant text into OpenAI's ChatGPT model and returns the output.


FaceDetector
Defined in: evadb/functions/face_detector.py
.. code:: mysql
   FaceDetector(data)
Finds faces within frames and returns bounding boxes indicating all of the found faces.


SiftFeatureExtractor
Defined in: evadb/functions/sift_feature_extractor.py
.. code:: mysql
   SiftFeatureExtractor(data)
Feature extracting function using the Kornia library to extract SIFT features from RGB images in a DataFrame.


StableDiffusion
Defined in: evadb/functions/stable_diffusion.py
.. code:: mysql
   StableDiffusion(prompt)
Generates images from textual prompts using an Replicate API.


DallE
Defined in: evadb/functions/dalle.py
.. code:: mysql
   DallE(prompt)
Generates images from textual prompts using an OpenAI API.


Upper
Defined in: evadb/functions/helpers/upper.py
.. code:: mysql
   Upper(text)
Helper function that converts an string to uppercase.


Lower
Defined in: evadb/functions/helpers/lower.py
.. code:: mysql
   Lower(text)
Helper function that converts an string to lowercase.


Concat
Defined in: evadb/functions/helpers/concat.py
.. code:: mysql
   concat(str1, str2)
Helper function that concatenates two strings.


