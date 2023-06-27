# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from evadb.configuration.constants import EvaDB_INSTALLATION_DIR
from evadb.database import EvaDBDatabase
from evadb.server.command_handler import execute_query_fetch_all

NDARRAY_DIR = "ndarray"
TUTORIALS_DIR = "tutorials"

DummyObjectDetector_udf_query = """CREATE UDF IF NOT EXISTS DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (label NDARRAY STR(1))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

DummyMultiObjectDetector_udf_query = """CREATE UDF
                  IF NOT EXISTS  DummyMultiObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(2))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

DummyFeatureExtractor_udf_query = """CREATE UDF
                  IF NOT EXISTS DummyFeatureExtractor
                  INPUT (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (features NDARRAY FLOAT32(1, ANYDIM))
                  TYPE Classification
                  IMPL '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

fuzzy_udf_query = """CREATE UDF IF NOT EXISTS FuzzDistance
                    INPUT (Input_Array1 NDARRAY ANYTYPE, Input_Array2 NDARRAY ANYTYPE)
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayUDF
                    IMPL "{}/udfs/{}/fuzzy_join.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

ArrayCount_udf_query = """CREATE UDF
            IF NOT EXISTS  ArrayCount
            INPUT (Input_Array NDARRAY ANYTYPE, Search_Key ANYTYPE)
            OUTPUT (key_count INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/array_count.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Crop_udf_query = """CREATE UDF IF NOT EXISTS Crop
                INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM),
                        bboxes NDARRAY FLOAT32(ANYDIM, 4))
                OUTPUT (Cropped_Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE  NdarrayUDF
                IMPL  "{}/udfs/{}/crop.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Open_udf_query = """CREATE UDF IF NOT EXISTS Open
                INPUT (img_path TEXT(1000))
                OUTPUT (data NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE NdarrayUDF
                IMPL "{}/udfs/{}/open.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Similarity_udf_query = """CREATE UDF IF NOT EXISTS Similarity
                    INPUT (Frame_Array_Open NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Frame_Array_Base NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Feature_Extractor_Name TEXT(100))
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayUDF
                    IMPL "{}/udfs/{}/similarity.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Unnest_udf_query = """CREATE UDF IF NOT EXISTS Unnest
                INPUT  (inp NDARRAY ANYTYPE)
                OUTPUT (out ANYTYPE)
                TYPE  NdarrayUDF
                IMPL  "{}/udfs/{}/unnest.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Fastrcnn_udf_query = """CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
      INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
      OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                scores NDARRAY FLOAT32(ANYDIM))
      TYPE  Classification
      IMPL  '{}/udfs/fastrcnn_object_detector.py';
      """.format(
    EvaDB_INSTALLATION_DIR
)

Yolo_udf_query = """CREATE UDF IF NOT EXISTS Yolo
      TYPE  ultralytics
      'model' 'yolov8m.pt';
      """

face_detection_udf_query = """CREATE UDF IF NOT EXISTS FaceDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  FaceDetection
                  IMPL  '{}/udfs/face_detector.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Mvit_udf_query = """CREATE UDF IF NOT EXISTS MVITActionRecognition
        INPUT  (Frame_Array NDARRAY UINT8(3, 16, 224, 224))
        OUTPUT (labels NDARRAY STR(ANYDIM))
        TYPE  Classification
        IMPL  '{}/udfs/mvit_action_recognition.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Asl_udf_query = """CREATE UDF IF NOT EXISTS ASLActionRecognition
        INPUT  (Frame_Array NDARRAY UINT8(3, 16, 224, 224))
        OUTPUT (labels NDARRAY STR(ANYDIM))
        TYPE  Classification
        IMPL  '{}/udfs/asl_action_recognition.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

norfair_obj_tracker_query = """CREATE UDF IF NOT EXISTS NorFairTracker
                  IMPL  '{}/udfs/trackers/nor_fair.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Sift_udf_query = """CREATE UDF IF NOT EXISTS SiftFeatureExtractor
        IMPL  '{}/udfs/sift_feature_extractor.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Text_feat_udf_query = """CREATE UDF IF NOT EXISTS SentenceFeatureExtractor
        IMPL  '{}/udfs/sentence_feature_extractor.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

mnistcnn_udf_query = """CREATE UDF IF NOT EXISTS MnistImageClassifier
        INPUT  (data NDARRAY (3, 28, 28))
        OUTPUT (label TEXT(2))
        TYPE  Classification
        IMPL  '{}/udfs/mnist_image_classifier.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

chatgpt_udf_query = """CREATE UDF IF NOT EXISTS ChatGPT
        IMPL '{}/udfs/chatgpt.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

yolo8n_query = """CREATE UDF IF NOT EXISTS Yolo
            TYPE  ultralytics
            'model' 'yolov8n.pt';
        """


def init_builtin_udfs(db: EvaDBDatabase, mode: str = "debug") -> None:
    """Load the built-in UDFs into the system during system bootstrapping.

    The function loads a set of pre-defined UDF queries based on the `mode` argument.
    In 'debug' mode, the function loads debug UDFs along with release UDFs.
    In 'release' mode, only release UDFs are loaded. In addition, in 'debug' mode,
    the function loads a smaller model to accelerate the test suite time.

    Args:
        mode (str, optional): The mode for loading UDFs, either 'debug' or 'release'.
        Defaults to 'debug'.

    """

    # Attempting to import torch module
    # It is necessary to import torch before to avoid encountering a
    # "RuntimeError: random_device could not be read"
    # The suspicion is that importing torch prior to decord resolves this issue
    try:
        import torch  # noqa: F401
    except ImportError:
        pass

    # Enable environment variables
    # Relevant for transformer-based models
    import os

    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # list of UDF queries to load
    queries = [
        mnistcnn_udf_query,
        Fastrcnn_udf_query,
        ArrayCount_udf_query,
        Crop_udf_query,
        Open_udf_query,
        Similarity_udf_query,
        norfair_obj_tracker_query,
        chatgpt_udf_query,
        face_detection_udf_query,
        # Mvit_udf_query,
        Sift_udf_query,
        Yolo_udf_query,
    ]

    # if mode is 'debug', add debug UDFs
    if mode == "debug":
        queries.extend(
            [
                DummyObjectDetector_udf_query,
                DummyMultiObjectDetector_udf_query,
                DummyFeatureExtractor_udf_query,
            ]
        )

    # execute each query in the list of UDF queries
    # ignore exceptions during the bootstrapping phase due to missing packages
    for query in queries:
        try:
            execute_query_fetch_all(
                db, query, do_not_print_exceptions=True, do_not_raise_exceptions=True
            )
        except Exception:
            pass
