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
from pprint import pprint

from evadb.parser.parser import Parser


class ParserStatementTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_parser_statement_types(self):
        parser = Parser()

        queries = [
            "CREATE INDEX testindex ON MyVideo (featCol) USING FAISS;",
            """CREATE TABLE IF NOT EXISTS Persons (
                  Frame_ID INTEGER UNIQUE,
                  Frame_Data TEXT(10),
                  Frame_Value FLOAT(1000, 201),
                  Frame_Array NDARRAY UINT8(5, 100, 2432, 4324, 100)
            )""",
            "RENAME TABLE student TO student_info",
            "DROP TABLE IF EXISTS student_info",
            "DROP TABLE student_info",
            "DROP UDF FastRCNN;",
            "SELECT MIN(id), MAX(id), SUM(id) FROM ABC",
            "SELECT CLASS FROM TAIPAI \
                WHERE (CLASS = 'VAN' AND REDNESS < 300)  OR REDNESS > 500;",
            "SELECT CLASS, REDNESS FROM TAIPAI \
            UNION ALL SELECT CLASS, REDNESS FROM SHANGHAI;",
            "SELECT CLASS, REDNESS FROM TAIPAI \
            UNION SELECT CLASS, REDNESS FROM SHANGHAI;",
            "SELECT FIRST(id) FROM TAIPAI GROUP BY '8 frames';",
            "SELECT CLASS, REDNESS FROM TAIPAI \
                    WHERE (CLASS = 'VAN' AND REDNESS < 400 ) OR REDNESS > 700 \
                    ORDER BY CLASS, REDNESS DESC;",
            "INSERT INTO MyVideo (Frame_ID, Frame_Path)\
                                    VALUES    (1, '/mnt/frames/1.png');",
            """INSERT INTO testDeleteOne (id, feat, salary, input)
                VALUES (15, 2.5, [[100, 100, 100]], [[100, 100, 100]]);""",
            """DELETE FROM Foo WHERE id < 6""",
            """LOAD VIDEO 'data/video.mp4' INTO MyVideo""",
            """LOAD IMAGE 'data/pic.jpg' INTO MyImage""",
            """LOAD CSV 'data/meta.csv' INTO
                             MyMeta (id, frame_id, video_id, label);""",
            """SELECT Licence_plate(bbox) FROM
                            (SELECT Yolo(frame).bbox FROM autonomous_vehicle_1
                              WHERE Yolo(frame).label = 'vehicle') AS T
                          WHERE Is_suspicious(bbox) = 1 AND
                                Licence_plate(bbox) = '12345';""",
            """CREATE MATERIALIZED VIEW uadtrac_fastRCNN (id, labels) AS
               SELECT id, Yolo(frame).labels FROM MyVideo
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
                  IMPL  'evadb/udfs/face_detector.py';
            """,
            "SHOW TABLES;",
            "SHOW UDFS;",
            "EXPLAIN SELECT a FROM foo;",
            """SELECT data FROM MyVideo WHERE id < 5
                    ORDER BY Similarity(FeatureExtractor(Open("abc.jpg")),
                                        FeatureExtractor(data))
                    LIMIT 1;""",
        ]
        # The queries below are the result of randomly changing the case of the
        # characters in the above queries.
        randomized_cases = [
            "Create index TestIndex on MyVideo (featCol) using FAISS;",
            """create table if not exists Persons (
                    Frame_ID integer unique,
                    Frame_Data text(10),
                    Frame_Value float(1000, 201),
                    Frame_Array ndArray uint8(5, 100, 2432, 4324, 100)
            )""",
            "Rename Table STUDENT to student_info",
            "drop table if exists Student_info",
            "drop table Student_Info",
            "Drop udf FASTRCNN;",
            "Select min(id), max(Id), Sum(Id) from ABC",
            "select CLASS from Taipai where (Class = 'VAN' and REDNESS < 300) or Redness > 500;",
            "select class, REDNESS from TAIPAI Union all select Class, redness from Shanghai;",
            "Select class, redness from Taipai Union Select CLASS, redness from Shanghai;",
            "Select first(Id) from Taipai group by '8F';",
            """Select Class, redness from TAIPAI
                where (CLASS = 'VAN' and redness < 400 ) or REDNESS > 700
                order by Class, redness DESC;""",
            "Insert into MyVideo (Frame_ID, Frame_Path) values (1, '/mnt/frames/1.png');",
            """insert into testDeleteOne (Id, feat, salary, input)
                values (15, 2.5, [[100, 100, 100]], [[100, 100, 100]]);""",
            "delete from Foo where ID < 6",
            "Load video 'data/video.mp4' into MyVideo",
            "Load image 'data/pic.jpg' into MyImage",
            """Load csv 'data/meta.csv' into
                MyMeta (id, Frame_ID, video_ID, label);""",
            """select Licence_plate(bbox) from
                (select Yolo(Frame).bbox from autonomous_vehicle_1
                where Yolo(frame).label = 'vehicle') as T
                where is_suspicious(bbox) = 1 and
                Licence_plate(bbox) = '12345';""",
            """Create materialized view UADTrac_FastRCNN (id, labels) as
                Select id, YoloV5(Frame).labels from MyVideo
                    where id<5; """,
            """Select Table1.A from Table1 join Table2
                on Table1.A = Table2.a where Table1.A <= 5""",
            """Select Table1.A from Table1 Join Table2
                    On Table1.a = Table2.A Join Table3
                On Table3.A = Table1.A where Table1.a <= 5""",
            """Select Frame from MyVideo Join Lateral
                ObjectDet(Frame) as OD;""",
            """Create UDF FaceDetector
                Input (Frame ndArray uint8(3, anydim, anydim))
                Output (bboxes ndArray float32(anydim, 4),
                scores ndArray float32(ANYdim))
                Type FaceDetection
                Impl 'evadb/udfs/face_detector.py';
            """,
        ]
        queries = queries + randomized_cases
        ref_stmt = parser.parse(queries[0])[0]
        self.assertNotEqual(ref_stmt, None)
        self.assertNotEqual(ref_stmt.__str__(), None)

        statement_to_query_dict = {}
        statement_to_query_dict[ref_stmt] = queries[0]

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
