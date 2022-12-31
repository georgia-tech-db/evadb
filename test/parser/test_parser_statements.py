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
import unittest
from pprint import pprint

from eva.parser.parser import Parser


class ParserStatementTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_parser_statement_types(self):
        parser = Parser()

        queries = [
            "CREATE INDEX testindex ON MyVideo (featCol) USING HNSW;",
            "RENAME TABLE student TO student_info",
            "DROP TABLE IF EXISTS student_info",
            "DROP UDF FastRCNN;",
            "SELECT CLASS FROM TAIPAI \
                WHERE (CLASS = 'VAN' AND REDNESS < 300)  OR REDNESS > 500;",
            "SELECT CLASS, REDNESS FROM TAIPAI \
            UNION ALL SELECT CLASS, REDNESS FROM SHANGHAI;",
            "SELECT FIRST(id) FROM TAIPAI GROUP BY '8f';",
            "SELECT CLASS, REDNESS FROM TAIPAI \
                    WHERE (CLASS = 'VAN' AND REDNESS < 400 ) OR REDNESS > 700 \
                    ORDER BY CLASS, REDNESS DESC;"
            "INSERT INTO MyVideo (Frame_ID, Frame_Path)\
                                    VALUES    (1, '/mnt/frames/1.png');",
            """LOAD VIDEO 'data/video.mp4' INTO MyVideo""",
            """LOAD IMAGE 'data/pic.jpg' INTO MyImage""",
            """LOAD CSV 'data/meta.csv' INTO
                             MyMeta (id, frame_id, video_id, label);""",
            """UPLOAD PATH 'data/video.mp4' BLOB "b'AAAA'"
                          INTO MyVideo WITH FORMAT VIDEO;""",
            """UPLOAD PATH 'data/meta.csv' BLOB "b'AAAA'"
                          INTO
                          MyMeta (id, frame_id, video_id, label)
                          WITH FORMAT CSV;""",
            """SELECT Licence_plate(bbox) FROM
                            (SELECT Yolo(frame).bbox FROM autonomous_vehicle_1
                              WHERE Yolo(frame).label = 'vehicle') AS T
                          WHERE Is_suspicious(bbox) = 1 AND
                                Licence_plate(bbox) = '12345';""",
            """CREATE MATERIALIZED VIEW uadtrac_fastRCNN (id, labels) AS
               SELECT id, YoloV5(frame).labels FROM MyVideo
                        WHERE id<5; """,
            """SELECT table1.a FROM table1 JOIN table2
            ON table1.a = table2.a WHERE table1.a <= 5""",
            """SELECT table1.a FROM table1 JOIN table2
            ON table1.a = table2.a JOIN table3
            ON table3.a = table1.a WHERE table1.a <= 5""",
            """SELECT frame FROM MyVideo JOIN LATERAL
                            ObjectDet(frame) AS OD;""",
            """CREATE UDF FaceDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  FaceDetection
                  IMPL  'eva/udfs/face_detector.py';
            """,
            "SHOW TABLES;",
            "SHOW UDFS",
            "EXPLAIN SELECT a FROM foo;",
            """SELECT data FROM MyVideo WHERE id < 5
                    ORDER BY Similarity(FeatureExtractor(Open("abc.jpg")),
                                        FeatureExtractor(data))
                    LIMIT 1;""",
        ]

        ref_stmt = parser.parse(queries[0])[0]
        self.assertNotEqual(ref_stmt, None)
        self.assertNotEqual(ref_stmt.__str__(), None)

        statement_to_query_dict = {}

        for other_query in queries[1:]:
            stmt = parser.parse(other_query)[0]

            pprint(str(stmt))

            # Check eq operator
            self.assertNotEqual(stmt, ref_stmt)
            self.assertEqual(stmt, stmt)
            self.assertNotEqual(stmt, None)

            # Check str operator
            self.assertNotEqual(stmt.__str__(), None)

            # Check hash operator
            statement_to_query_dict[stmt] = other_query
