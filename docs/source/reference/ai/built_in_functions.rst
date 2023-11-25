Built-In Functions
==================

MnistImageClassifier
--------------------
- **Defined in:** evadb/functions/mnist_image_classifier.py
- **Usage:** `MnistImageClassifier(input).label`
- **Description:** Recognizes and classifies images of handwritten numbers.

FastRCNNObjectDetector
----------------------
- **Defined in:** evadb/functions/fastrcnn_object_detector.py
- **Usage:** ``FastRCNNObjectDetector(frame).labels``
- **Description:** Recognizes and classifies objects.

ArrayCount
-----------
- **Defined in:** evadb/functions/ndarray/array_count.py
- **Usage:** ``ArrayCount(input_frame, search_key)``
- **Description:** Returns the number of times that the given search key was found in the input frame.

Crop
-----
- **Defined in:** evadb/functions/ndarray/crop.py
- **Usage:** ``Crop(data, bbox)``
- **Description:** Crops input frames based upon the bounding box coordinates and returns the cropped version.

Open
-----
- **Defined in:** evadb/functions/ndarray/open.py
- **Usage:** ``Open(image_path)``
- **Description:** Opens and caches an image. Returns a data frame containing the image.

Similarity
-----------
- **Defined in:** evadb/functions/ndarray/similarity.py
- **Usage:** ``Similarity(frame1, frame2)``
- **Description:** Returns a similarity score between two feature vectors.

ChatGPT
-------
- **Defined in:** evadb/functions/chatgpt.py
- **Usage:** ``ChatGPT(query, text)``
- **Description:** Passes the query and relevant text into OpenAI's ChatGPT model and returns the output.

FaceDetector
-------------
- **Defined in:** evadb/functions/face_detector.py
- **Usage:** ``FaceDetector(data)``
- **Description:** Finds faces within frames and returns bounding boxes indicating all of the found faces.

SiftFeatureExtractor
---------------------
- **Defined in:** evadb/functions/sift_feature_extractor.py
- **Usage:** ``SiftFeatureExtractor(data)``
- **Description:** Feature extracting function using the Kornia library to extract SIFT features from RGB images in a DataFrame.

StableDiffusion
----------------
- **Defined in:** evadb/functions/stable_diffusion.py
- **Usage:** ``StableDiffusion(prompt)``
- **Description:** Generates images from textual prompts using a Replicate API.

DallE
------
- **Defined in:** evadb/functions/dalle.py
- **Usage:** ``DallE(prompt)``
- **Description:** Generates images from textual prompts using an OpenAI API.

Upper
-----
- **Defined in:** evadb/functions/helpers/upper.py
- **Usage:** ``Upper(text)``
- **Description:** Helper function that converts a string to uppercase.

Lower
-----
- **Defined in:** evadb/functions/helpers/lower.py
- **Usage:** ``Lower(text)``
- **Description:** Helper function that converts a string to lowercase.

Concat
------
- **Defined in:** evadb/functions/helpers/concat.py
- **Usage:** ``concat(str1, str2)``
- **Description:** Helper function that concatenates two strings.
