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
import base64
import os
import shutil
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from eva.binder.statement_binder import StatementBinder
from eva.binder.statement_binder_context import StatementBinderContext
from eva.configuration.configuration_manager import ConfigurationManager
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.models.storage.batch import Batch
from eva.optimizer.operators import Operator
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from eva.parser.parser import Parser
from eva.planner.abstract_plan import AbstractPlan
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.udfs.udf_bootstrap_queries import init_builtin_udfs

NUM_FRAMES = 10
FRAME_SIZE = 2 * 2 * 3
config = ConfigurationManager()
upload_dir_from_config = config.get_value("storage", "upload_dir")


EVA_TEST_DATA_DIR = Path(config.get_value("core", "eva_installation_dir")).parent


def get_logical_query_plan(query: str) -> Operator:
    """Get the query plan

    Args:
        query (str): evaql query

    Returns:
        Operator: Logical plan generated by eva
    """
    stmt = Parser().parse(query)[0]
    StatementBinder(StatementBinderContext()).bind(stmt)
    l_plan = StatementToPlanConvertor().visit(stmt)
    return l_plan


def get_physical_query_plan(
    query: str, rule_manager=None, cost_model=None
) -> AbstractPlan:
    """Get the query plan

    Args:
        query (str): evaql query

    Returns:
        AbstractPlan: Optimal query plan generated by optimizer
    """
    l_plan = get_logical_query_plan(query)
    p_plan = PlanGenerator(rule_manager, cost_model).build(l_plan)
    return p_plan


def create_dataframe(num_frames=1) -> pd.DataFrame:
    frames = []
    for i in range(1, num_frames + 1):
        frames.append({"id": i, "data": (i * np.ones((1, 1)))})
    return pd.DataFrame(frames)


def create_dataframe_same(times=1):
    base_df = create_dataframe()
    for i in range(1, times):
        base_df = base_df.append(create_dataframe(), ignore_index=True)
    return base_df


def custom_list_of_dicts_equal(one, two):
    for v1, v2 in zip(one, two):
        if v1.keys() != v2.keys():
            return False
        for key in v1.keys():
            if isinstance(v1[key], np.ndarray):
                if not np.array_equal(v1[key], v2[key]):
                    return False

            else:
                if v1[key] != v2[key]:
                    return False

    return True


def convert_bbox(bbox):
    return np.array([np.float32(coord) for coord in bbox.split(",")])


def create_sample_csv(num_frames=NUM_FRAMES):
    try:
        os.remove(os.path.join(upload_dir_from_config, "dummy.csv"))
    except FileNotFoundError:
        pass

    sample_meta = {}

    index = 0
    sample_labels = ["car", "pedestrian", "bicycle"]
    num_videos = 2
    for video_id in range(num_videos):
        for frame_id in range(num_frames):
            random_coords = 200 + 300 * np.random.random(4)
            sample_meta[index] = {
                "id": index,
                "frame_id": frame_id,
                "video_id": video_id,
                "dataset_name": "test_dataset",
                "label": sample_labels[np.random.choice(len(sample_labels))],
                "bbox": ",".join([str(coord) for coord in random_coords]),
                "object_id": np.random.choice(3),
            }

            index += 1

    df_sample_meta = pd.DataFrame.from_dict(sample_meta, "index")
    df_sample_meta.to_csv(
        os.path.join(upload_dir_from_config, "dummy.csv"), index=False
    )


def create_sample_csv_as_blob(num_frames=NUM_FRAMES):
    try:
        os.remove(os.path.join(upload_dir_from_config, "dummy.csv"))
    except FileNotFoundError:
        pass

    sample_meta = {}

    index = 0
    sample_labels = ["car", "pedestrian", "bicycle"]
    num_videos = 2
    for video_id in range(num_videos):
        for frame_id in range(num_frames):
            random_coords = 200 + 300 * np.random.random(4)
            sample_meta[index] = {
                "id": index,
                "frame_id": frame_id,
                "video_id": video_id,
                "dataset_name": "test_dataset",
                "label": sample_labels[np.random.choice(len(sample_labels))],
                "bbox": ",".join([str(coord) for coord in random_coords]),
                "object_id": np.random.choice(3),
            }

            index += 1

    df_sample_meta = pd.DataFrame.from_dict(sample_meta, "index")
    df_sample_meta.to_csv(
        os.path.join(upload_dir_from_config, "dummy.csv"), index=False
    )

    with open(os.path.join(upload_dir_from_config, "dummy.csv"), "rb") as f:
        bytes_read = f.read()
        b64_string = str(base64.b64encode(bytes_read))
    return b64_string


def create_dummy_csv_batches(target_columns=None):

    if target_columns:
        df = pd.read_csv(
            os.path.join(upload_dir_from_config, "dummy.csv"),
            converters={"bbox": convert_bbox},
            usecols=target_columns,
        )
    else:
        df = pd.read_csv(
            os.path.join(upload_dir_from_config, "dummy.csv"),
            converters={"bbox": convert_bbox},
        )

    return Batch(df)


def create_csv(num_rows, columns):
    try:
        os.remove(os.path.join(upload_dir_from_config, "dummy.csv"))
    except FileNotFoundError:
        pass
    df = pd.DataFrame(columns=columns)
    for col in columns:
        df[col] = np.random.randint(1, 100, num_rows)
    df.to_csv(os.path.join(upload_dir_from_config, "dummy.csv"), index=False)
    return df


def create_table(table_name, num_rows, num_columns):
    # creates a table with num_rows tuples and columns = [a1, a2, a3, ...]
    columns = "".join("a{} INTEGER, ".format(i) for i in range(num_columns - 1))
    columns += "a{} INTEGER".format(num_columns - 1)
    create_table_query = "CREATE TABLE IF NOT EXISTS {} ( {} );".format(
        table_name, columns
    )
    execute_query_fetch_all(create_table_query)
    columns = ["a{}".format(i) for i in range(num_columns)]
    df = create_csv(num_rows, columns)
    # load the CSV
    load_query = """LOAD CSV 'dummy.csv' INTO {};""".format(table_name)
    execute_query_fetch_all(load_query)
    df.columns = [f"{table_name}.{col}" for col in df.columns]
    return df


def create_sample_video(num_frames=NUM_FRAMES):
    try:
        os.remove(os.path.join(upload_dir_from_config, "dummy.avi"))
    except FileNotFoundError:
        pass

    out = cv2.VideoWriter(
        os.path.join(upload_dir_from_config, "dummy.avi"),
        cv2.VideoWriter_fourcc("M", "J", "P", "G"),
        10,
        (2, 2),
    )
    for i in range(num_frames):
        frame = np.array(np.ones((2, 2, 3)) * float(i + 1) * 25, dtype=np.uint8)
        out.write(frame)

    out.release()


def create_sample_video_as_blob(num_frames=NUM_FRAMES):
    try:
        os.remove(os.path.join(upload_dir_from_config, "dummy.avi"))
    except FileNotFoundError:
        pass

    out = cv2.VideoWriter(
        os.path.join(upload_dir_from_config, "dummy.avi"),
        cv2.VideoWriter_fourcc("M", "J", "P", "G"),
        10,
        (2, 2),
    )
    for i in range(num_frames):
        frame = np.array(np.ones((2, 2, 3)) * float(i + 1) * 25, dtype=np.uint8)
        out.write(frame)

    out.release()

    with open(os.path.join(upload_dir_from_config, "dummy.avi"), "rb") as f:
        bytes_read = f.read()
        b64_string = str(base64.b64encode(bytes_read))
    return b64_string


def copy_sample_videos_to_upload_dir():
    shutil.copyfile(
        "data/ua_detrac/ua_detrac.mp4",
        os.path.join(upload_dir_from_config, "ua_detrac.mp4"),
    )
    shutil.copyfile(
        "data/mnist/mnist.mp4",
        os.path.join(upload_dir_from_config, "mnist.mp4"),
    )
    shutil.copyfile(
        "data/actions/actions.mp4",
        os.path.join(upload_dir_from_config, "actions.mp4"),
    )


def file_remove(path):
    os.remove(os.path.join(upload_dir_from_config, path))


def create_dummy_batches(num_frames=NUM_FRAMES, filters=[], batch_size=10, start_id=0):
    if not filters:
        filters = range(num_frames)
    data = []
    for i in filters:
        data.append(
            {
                "myvideo.name": "dummy.avi",
                "myvideo.id": i + start_id,
                "myvideo.data": np.array(
                    np.ones((2, 2, 3)) * float(i + 1) * 25, dtype=np.uint8
                ),
            }
        )

        if len(data) % batch_size == 0:
            yield Batch(pd.DataFrame(data))
            data = []
    if data:
        yield Batch(pd.DataFrame(data))


def create_dummy_4d_batches(
    num_frames=NUM_FRAMES, filters=[], batch_size=10, start_id=0
):
    if not filters:
        filters = range(num_frames)
    data = []
    for segment in filters:
        segment_data = []
        for i in segment:
            segment_data.append(np.ones((2, 2, 3)) * float(i + 1) * 25)
        segment_data = np.stack(np.array(segment_data, dtype=np.uint8))
        data.append(
            {
                "myvideo.name": "dummy.avi",
                "myvideo.id": segment[0] + start_id,
                "myvideo.data": segment_data,
            }
        )

        if len(data) % batch_size == 0:
            yield Batch(pd.DataFrame(data))
            data = []
    if data:
        yield Batch(pd.DataFrame(data))


def load_inbuilt_udfs():
    mode = ConfigurationManager().get_value("core", "mode")
    init_builtin_udfs(mode=mode)


class DummyObjectDetector(AbstractClassifierUDF):
    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyObjectDetector"

    @property
    def input_format(self):
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self):
        return ["__background__", "person", "bicycle"]

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["label"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        i = int(frames[0][0][0][0] * 25) - 1
        label = self.labels[i % 2 + 1]
        return np.array([label])


class DummyMultiObjectDetector(AbstractClassifierUDF):
    """
    Returns multiple objects for each frame
    """

    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyMultiObjectDetector"

    @property
    def input_format(self):
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self):
        return ["__background__", "person", "bicycle", "car"]

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["labels"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        i = int(frames[0][0][0][0] * 25) - 1
        label = self.labels[i % 3 + 1]
        return np.array([label, label])
