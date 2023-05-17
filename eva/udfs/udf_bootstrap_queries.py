# coding=utf-8
# Copyright 2018-2022 EVA
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

from eva.configuration.configuration_manager import ConfigurationManager
from eva.server.command_handler import execute_query_fetch_all

EVA_INSTALLATION_DIR = ConfigurationManager().get_value("core", "eva_installation_dir")
NDARRAY_DIR = "ndarray"

DummyObjectDetector_udf_query = """CREATE UDF IF NOT EXISTS DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (label NDARRAY STR(1))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EVA_INSTALLATION_DIR
)

DummyMultiObjectDetector_udf_query = """CREATE UDF
                  IF NOT EXISTS  DummyMultiObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(2))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EVA_INSTALLATION_DIR
)

DummyFeatureExtractor_udf_query = """CREATE UDF
                  IF NOT EXISTS DummyFeatureExtractor
                  INPUT (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (features NDARRAY FLOAT32(1, ANYDIM))
                  TYPE Classification
                  IMPL '{}/../test/util.py';
        """.format(
    EVA_INSTALLATION_DIR
)

ArrayCount_udf_query = """CREATE UDF
            IF NOT EXISTS  ArrayCount
            INPUT (Input_Array NDARRAY ANYTYPE, Search_Key ANYTYPE)
            OUTPUT (key_count INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/array_count.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Crop_udf_query = """CREATE UDF IF NOT EXISTS Crop
                INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM),
                        bboxes NDARRAY FLOAT32(ANYDIM, 4))
                OUTPUT (Cropped_Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE  NdarrayUDF
                IMPL  "{}/udfs/{}/crop.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Open_udf_query = """CREATE UDF IF NOT EXISTS Open
                INPUT (img_path TEXT(1000))
                OUTPUT (data NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE NdarrayUDF
                IMPL "{}/udfs/{}/open.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Similarity_udf_query = """CREATE UDF IF NOT EXISTS Similarity
                    INPUT (Frame_Array_Open NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Frame_Array_Base NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Feature_Extractor_Name TEXT(100))
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayUDF
                    IMPL "{}/udfs/{}/similarity.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Unnest_udf_query = """CREATE UDF IF NOT EXISTS Unnest
                INPUT  (inp NDARRAY ANYTYPE)
                OUTPUT (out ANYTYPE)
                TYPE  NdarrayUDF
                IMPL  "{}/udfs/{}/unnest.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Fastrcnn_udf_query = """CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
      INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
      OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                scores NDARRAY FLOAT32(ANYDIM))
      TYPE  Classification
      IMPL  '{}/udfs/fastrcnn_object_detector.py';
      """.format(
    EVA_INSTALLATION_DIR
)

Yolo_udf_query = """CREATE UDF IF NOT EXISTS Yolo
      TYPE  ultralytics
      'model' 'yolov8m.pt';
      """

ocr_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
      INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
      OUTPUT (labels NDARRAY STR(10), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                scores NDARRAY FLOAT32(ANYDIM))
      TYPE  OCRExtraction
      IMPL  '{}/udfs/ocr_extractor.py';
      """.format(
    EVA_INSTALLATION_DIR
)

face_detection_udf_query = """CREATE UDF IF NOT EXISTS FaceDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  FaceDetection
                  IMPL  '{}/udfs/face_detector.py';
        """.format(
    EVA_INSTALLATION_DIR
)

Mvit_udf_query = """CREATE UDF IF NOT EXISTS MVITActionRecognition
        INPUT  (Frame_Array NDARRAY UINT8(3, 16, 224, 224))
        OUTPUT (labels NDARRAY STR(ANYDIM))
        TYPE  Classification
        IMPL  '{}/udfs/mvit_action_recognition.py';
        """.format(
    EVA_INSTALLATION_DIR
)

Asl_udf_query = """CREATE UDF IF NOT EXISTS ASLActionRecognition
        INPUT  (Frame_Array NDARRAY UINT8(3, 16, 224, 224))
        OUTPUT (labels NDARRAY STR(ANYDIM))
        TYPE  Classification
        IMPL  '{}/udfs/asl_action_recognition.py';
        """.format(
    EVA_INSTALLATION_DIR
)


norfair_obj_tracker_query = """CREATE UDF IF NOT EXISTS NorFairTracker
                  IMPL  '{}/udfs/trackers/nor_fair.py';
        """.format(
    EVA_INSTALLATION_DIR
)

Sift_udf_query = """CREATE UDF IF NOT EXISTS SiftFeatureExtractor
        IMPL  '{}/udfs/sift_feature_extractor.py';
        """.format(
    EVA_INSTALLATION_DIR
)


def init_builtin_udfs(mode: str = "debug") -> None:
    """Load the built-in UDFs into the system during system bootstrapping.

    The function loads a set of pre-defined UDF queries based on the `mode` argument.
    In 'debug' mode, the function loads debug UDFs along with release UDFs.
    In 'release' mode, only release UDFs are loaded. In addition, in 'debug' mode,
    the function loads a smaller model to accelerate the test suite time.

    Args:
        mode (str, optional): The mode for loading UDFs, either 'debug' or 'release'.
        Defaults to 'debug'.

    """
    # list of UDF queries to load
    queries = [
        Fastrcnn_udf_query,
        ArrayCount_udf_query,
        Crop_udf_query,
        Open_udf_query,
        Similarity_udf_query,
        norfair_obj_tracker_query,
        # Disabled because required packages (eg., easy_ocr might not be preinstalled)
        # face_detection_udf_query,
        # ocr_udf_query,
        # Mvit_udf_query, - Disabled as it requires specific pytorch package
        # Sift_udf_query, - requires package kornia
    ]

    if mode == "release":
        # if mode is 'release', add the Yolo query to the list
        queries.append(Yolo_udf_query)
    else:
        # if mode is 'debug', add debug UDFs and a smaller Yolo model
        queries.extend(
            [
                DummyObjectDetector_udf_query,
                DummyMultiObjectDetector_udf_query,
                DummyFeatureExtractor_udf_query,
            ]
        )

        yolo8n = """CREATE UDF IF NOT EXISTS Yolo
            TYPE  ultralytics
            'model' 'yolov8n.pt';
        """
        queries.append(yolo8n)

    # execute each query in the list of UDF queries
    for query in queries:
        execute_query_fetch_all(query)
