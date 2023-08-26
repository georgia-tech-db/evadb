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
import unittest
from test.util import create_text_csv, file_remove, get_evadb_for_testing

import pytest

from evadb.executor.executor_utils import ExecutorError
from evadb.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


class HuggingFaceTests(unittest.TestCase):
    """
    The tests below essentially check for the output format returned by HF.
    We need to ensure that it is in the format that we expect.
    """

    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()

        # Use DETRAC for HF Tests to test variety of models
        query = """LOAD VIDEO 'data/ua_detrac/ua_detrac.mp4' INTO DETRAC;"""
        execute_query_fetch_all(self.evadb, query)

        query = """LOAD VIDEO 'data/sample_videos/touchdown.mp4' INTO VIDEOS"""
        execute_query_fetch_all(self.evadb, query)

        query = """LOAD PDF 'data/documents/pdf_sample1.pdf' INTO MyPDFs;"""
        execute_query_fetch_all(self.evadb, query)
        # Text CSV for testing HF Text Based Models
        self.csv_file_path = create_text_csv()

    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS DETRAC;")
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS VIDEOS;")
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyCSV;")
        file_remove(self.csv_file_path)

    def test_io_catalog_entries_populated(self):
        udf_name, task = "HFObjectDetector", "image-classification"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' '{task}'
        """

        execute_query_fetch_all(self.evadb, create_udf_query)

        catalog = self.evadb.catalog()
        udf = catalog.get_udf_catalog_entry_by_name(udf_name)
        input_entries = catalog.get_udf_io_catalog_input_entries(udf)
        output_entries = catalog.get_udf_io_catalog_output_entries(udf)

        # Verify that there is one input entry with the name text
        self.assertEqual(len(input_entries), 1)
        self.assertEqual(input_entries[0].name, f"{udf_name}_IMAGE")

        # Verify that there are 3 output entries with the names score, label and box
        self.assertEqual(len(output_entries), 2)
        self.assertEqual(output_entries[0].name, "score")
        self.assertEqual(output_entries[1].name, "label")

    def test_raise_error_on_unsupported_task(self):
        udf_name = "HFUnsupportedTask"
        task = "zero-shot-object-detection"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' '{task}'
        """
        # catch an assert

        with self.assertRaises(ExecutorError) as exc_info:
            execute_query_fetch_all(
                self.evadb, create_udf_query, do_not_print_exceptions=True
            )
        self.assertIn(
            f"Task {task} not supported in EvaDB currently", str(exc_info.exception)
        )

    def test_object_detection(self):
        udf_name = "HFObjectDetector"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'object-detection'
            'model' 'facebook/detr-resnet-50';
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = f"SELECT {udf_name}(data) FROM DETRAC WHERE id < 4;"
        output = execute_query_fetch_all(self.evadb, select_query)
        output_frames = output.frames

        # Test that output has 3 columns
        self.assertEqual(len(output_frames.columns), 3)

        # Test that number of rows is equal to 10
        self.assertEqual(len(output.frames), 4)

        # Test that there exists a column with udf_name.score and each entry is a list of floats
        self.assertTrue(udf_name.lower() + ".score" in output_frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".score"])
        )

        # Test that there exists a column with udf_name.label and each entry is a list of strings
        self.assertTrue(udf_name.lower() + ".label" in output_frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".label"])
        )

        # Test that there exists a column with udf_name.box and each entry is a dictionary with 4 keys
        self.assertTrue(udf_name.lower() + ".box" in output_frames.columns)
        for bbox in output.frames[udf_name.lower() + ".box"]:
            self.assertTrue(isinstance(bbox, list))
            bbox = bbox[0]
            self.assertTrue(isinstance(bbox, dict))
            self.assertTrue(len(bbox) == 4)
            self.assertTrue("xmin" in bbox)
            self.assertTrue("ymin" in bbox)
            self.assertTrue("xmax" in bbox)
            self.assertTrue("ymax" in bbox)

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)

    def test_image_classification(self):
        udf_name = "HFImageClassifier"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'image-classification'
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = f"SELECT {udf_name}(data) FROM DETRAC WHERE id < 3;"
        output = execute_query_fetch_all(self.evadb, select_query)

        # Test that output has 2 columns
        self.assertEqual(len(output.frames.columns), 2)

        # Test that there exists a column with udf_name.score and each entry is a list of floats
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".score"])
        )

        # Test that there exists a column with udf_name.label and each entry is a list of strings
        self.assertTrue(udf_name.lower() + ".label" in output.frames.columns)
        self.assertTrue(
            all(isinstance(x, list) for x in output.frames[udf_name.lower() + ".label"])
        )

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)

    @pytest.mark.benchmark
    def test_text_classification(self):
        create_table_query = """CREATE TABLE IF NOT EXISTS MyCSV (
                id INTEGER UNIQUE,
                comment TEXT(30)
            );"""
        execute_query_fetch_all(self.evadb, create_table_query)

        load_table_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyCSV;"""
        execute_query_fetch_all(self.evadb, load_table_query)

        udf_name = "HFTextClassifier"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'text-classification'
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        select_query = f"SELECT {udf_name}(comment) FROM MyCSV;"
        output = execute_query_fetch_all(self.evadb, select_query)

        # Test that output has 2 columns
        self.assertEqual(len(output.frames.columns), 2)

        # Test that there exists a column with udf_name.label and each entry is either "POSITIVE" or "NEGATIVE"
        self.assertTrue(udf_name.lower() + ".label" in output.frames.columns)
        self.assertTrue(
            all(
                x in ["POSITIVE", "NEGATIVE"]
                for x in output.frames[udf_name.lower() + ".label"]
            )
        )

        # Test that there exists a column with udf_name.score and each entry is a float
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)
        self.assertTrue(
            all(
                isinstance(x, float) for x in output.frames[udf_name.lower() + ".score"]
            )
        )

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)
        execute_query_fetch_all(self.evadb, "DROP TABLE MyCSV;")

    @pytest.mark.benchmark
    def test_automatic_speech_recognition(self):
        udf_name = "SpeechRecognizer"
        create_udf = (
            f"CREATE UDF {udf_name} TYPE HuggingFace "
            "'task' 'automatic-speech-recognition' 'model' 'openai/whisper-base';"
        )
        execute_query_fetch_all(self.evadb, create_udf)

        # TODO: use with SAMPLE AUDIORATE 16000
        select_query = f"SELECT {udf_name}(audio) FROM VIDEOS;"
        output = execute_query_fetch_all(self.evadb, select_query)

        # verify that output has one row and one column only
        self.assertTrue(output.frames.shape == (1, 1))
        # verify that speech was converted to text correctly
        self.assertTrue(output.frames.iloc[0][0].count("touchdown") == 2)

        select_query_with_group_by = (
            f"SELECT {udf_name}(SEGMENT(audio)) FROM VIDEOS GROUP BY '240 samples';"
        )
        output = execute_query_fetch_all(self.evadb, select_query_with_group_by)

        # verify that output has one row and one column only
        self.assertEquals(output.frames.shape, (4, 1))
        # verify that speech was converted to text correctly
        self.assertEquals(output.frames.iloc[0][0].count("touchdown"), 1)

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)

    @pytest.mark.benchmark
    def test_summarization_from_video(self):
        asr_udf = "SpeechRecognizer"
        create_udf = (
            f"CREATE UDF {asr_udf} TYPE HuggingFace "
            "'task' 'automatic-speech-recognition' 'model' 'openai/whisper-base';"
        )
        execute_query_fetch_all(self.evadb, create_udf)

        summary_udf = "Summarizer"
        create_udf = (
            f"CREATE UDF {summary_udf} TYPE HuggingFace "
            "'task' 'summarization' 'model' 'philschmid/bart-large-cnn-samsum' 'min_length' 10 'max_new_tokens' 100;"
        )
        execute_query_fetch_all(self.evadb, create_udf)

        # TODO: use with SAMPLE AUDIORATE 16000
        select_query = f"SELECT {summary_udf}({asr_udf}(audio)) FROM VIDEOS;"
        output = execute_query_fetch_all(self.evadb, select_query)

        # verify that output has one row and one column only
        self.assertTrue(output.frames.shape == (1, 1))
        # verify that summary is as expected
        self.assertTrue(
            output.frames.iloc[0][0]
            == "Jalen Hurts has scored his second rushing touchdown of the game."
        )

        drop_udf_query = f"DROP UDF {asr_udf};"
        execute_query_fetch_all(self.evadb, drop_udf_query)
        drop_udf_query = f"DROP UDF {summary_udf};"
        execute_query_fetch_all(self.evadb, drop_udf_query)

    def test_toxicity_classification(self):
        udf_name = "HFToxicityClassifier"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'text-classification'
            'model' 'martin-ha/toxic-comment-model'
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        drop_table_query = """DROP TABLE IF EXISTS MyCSV;"""
        execute_query_fetch_all(self.evadb, drop_table_query)

        create_table_query = """CREATE TABLE IF NOT EXISTS MyCSV (
                id INTEGER UNIQUE,
                comment TEXT(30)
            );"""
        execute_query_fetch_all(self.evadb, create_table_query)

        load_table_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyCSV;"""
        execute_query_fetch_all(self.evadb, load_table_query)

        select_query = f"SELECT {udf_name}(comment) FROM MyCSV;"
        output = execute_query_fetch_all(self.evadb, select_query)

        # Test that output has 2 columns
        self.assertEqual(len(output.frames.columns), 2)

        # Test that there exists a column with udf_name.label and each entry is either "POSITIVE" or "NEGATIVE"
        self.assertTrue(udf_name.lower() + ".label" in output.frames.columns)
        self.assertTrue(
            all(
                x in ["non-toxic", "toxic"]
                for x in output.frames[udf_name.lower() + ".label"]
            )
        )

        # Test that there exists a column with udf_name.score
        # and each entry is a float
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)
        self.assertTrue(
            all(
                isinstance(x, float) for x in output.frames[udf_name.lower() + ".score"]
            )
        )

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)

    @pytest.mark.benchmark
    def test_multilingual_toxicity_classification(self):
        udf_name = "HFMultToxicityClassifier"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'text-classification'
            'model' 'EIStakovskii/xlm_roberta_base_multilingual_toxicity_classifier_plus'
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        drop_table_query = """DROP TABLE IF EXISTS MyCSV;"""
        execute_query_fetch_all(self.evadb, drop_table_query)

        create_table_query = """CREATE TABLE MyCSV (
                id INTEGER UNIQUE,
                comment TEXT(30)
            );"""
        execute_query_fetch_all(self.evadb, create_table_query)

        load_table_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyCSV;"""
        execute_query_fetch_all(self.evadb, load_table_query)

        select_query = f"SELECT {udf_name}(comment) FROM MyCSV;"
        output = execute_query_fetch_all(self.evadb, select_query)

        # Test that output has 2 columns
        self.assertEqual(len(output.frames.columns), 2)

        # Test that there exists a column with udf_name.label and each entry is either "POSITIVE" or "NEGATIVE"
        self.assertTrue(udf_name.lower() + ".label" in output.frames.columns)
        self.assertTrue(
            all(
                x in ["LABEL_1", "LABEL_0"]
                for x in output.frames[udf_name.lower() + ".label"]
            )
        )

        # Test that there exists a column with udf_name.score and each entry is a float
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)
        self.assertTrue(
            all(
                isinstance(x, float) for x in output.frames[udf_name.lower() + ".score"]
            )
        )

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)

    @pytest.mark.benchmark
    def test_named_entity_recognition_model_all_pdf_data(self):
        udf_name = "HFNERModel"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'ner'
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        # running test case on all the pdf data
        select_query = f"SELECT data, {udf_name}(data) FROM MyPDFs;"
        output = execute_query_fetch_all(self.evadb, select_query)

        # Test that output has 7 columns
        self.assertEqual(len(output.frames.columns), 7)

        # Test that there exists a column with udf_name.entity
        self.assertTrue(udf_name.lower() + ".entity" in output.frames.columns)

        # Test that there exists a column with udf_name.score
        self.assertTrue(udf_name.lower() + ".score" in output.frames.columns)

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)

    def test_select_and_groupby_with_paragraphs(self):
        segment_size = 10
        select_query = (
            "SELECT SEGMENT(data) FROM MyPDFs GROUP BY '{}paragraphs';".format(
                segment_size
            )
        )
        output = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(len(output.frames), 3)

    @pytest.mark.benchmark
    def test_named_entity_recognition_model_no_ner_data_exists(self):
        udf_name = "HFNERModel"
        create_udf_query = f"""CREATE UDF {udf_name}
            TYPE HuggingFace
            'task' 'ner'
        """
        execute_query_fetch_all(self.evadb, create_udf_query)

        # running test case where ner gives no data
        select_query = f"""SELECT data, {udf_name}(data)
                  FROM MyPDFs
                  WHERE page = 3
                  AND paragraph >= 1 AND paragraph <= 3;"""
        output = execute_query_fetch_all(self.evadb, select_query)

        # Test that output only has 1 column (data)
        self.assertEqual(len(output.frames.columns), 1)

        # Test that there does not exist a column with udf_name.entity
        self.assertFalse(udf_name.lower() + ".entity" in output.frames.columns)

        drop_udf_query = f"DROP UDF {udf_name};"
        execute_query_fetch_all(self.evadb, drop_udf_query)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(HuggingFaceTests("test_automatic_speech_recognition"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
