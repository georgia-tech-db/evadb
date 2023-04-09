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
import os
import socket
from contextlib import closing
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import psutil
import ray
from mock import MagicMock

from eva.binder.statement_binder import StatementBinder
from eva.binder.statement_binder_context import StatementBinderContext
from eva.catalog.catalog_type import NdArrayType
from eva.configuration.configuration_manager import ConfigurationManager
from eva.models.storage.batch import Batch
from eva.optimizer.operators import Operator
from eva.optimizer.plan_generator import PlanGenerator
from eva.optimizer.statement_to_opr_convertor import StatementToPlanConvertor
from eva.parser.parser import Parser
from eva.plan_nodes.abstract_plan import AbstractPlan
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.abstract.abstract_udf import AbstractClassifierUDF
from eva.udfs.decorators import decorators
from eva.udfs.decorators.io_descriptors.data_types import NumpyArray, PandasDataframe
from eva.udfs.udf_bootstrap_queries import init_builtin_udfs

NUM_FRAMES = 10
FRAME_SIZE = (32, 32)
config = ConfigurationManager()
tmp_dir_from_config = config.get_value("storage", "tmp_dir")
s3_dir_from_config = config.get_value("storage", "s3_download_dir")


EVA_TEST_DATA_DIR = Path(config.get_value("core", "eva_installation_dir")).parent


def is_ray_stage_running():
    return "ray::ray_stage" in (p.name() for p in psutil.process_iter())


def shutdown_ray():
    if ConfigurationManager().get_value("experimental", "ray"):
        ray.shutdown()


def prefix_worker_id(base: str):
    try:
        worker_id = os.environ["PYTEST_XDIST_WORKER"]
        prefixed_base = str(worker_id) + "_" + base
    except KeyError:
        # Single threaded mode
        prefixed_base = base
    return prefixed_base


# Ref: https://stackoverflow.com/a/63851681
def get_all_subclasses(cls):
    subclass_list = []

    def recurse(klass):
        for subclass in klass.__subclasses__():
            subclass_list.append(subclass)
            recurse(subclass)

    recurse(cls)

    return set(subclass_list)


def get_mock_object(class_type, number_of_args):
    if number_of_args == 1:
        return class_type()
    elif number_of_args == 2:
        return class_type(MagicMock())
    elif number_of_args == 3:
        return class_type(MagicMock(), MagicMock())
    elif number_of_args == 4:
        return class_type(MagicMock(), MagicMock(), MagicMock())
    elif number_of_args == 5:
        return class_type(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    elif number_of_args == 6:
        return class_type(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
    elif number_of_args == 7:
        return class_type(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
    elif number_of_args == 8:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 9:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 10:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 11:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 12:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    else:
        raise Exception("Too many args")


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


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
        base_df = pd.concat([base_df, create_dataframe()], ignore_index=True)
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
        os.remove(os.path.join(tmp_dir_from_config, "dummy.csv"))
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
    df_sample_meta.to_csv(os.path.join(tmp_dir_from_config, "dummy.csv"), index=False)
    return os.path.join(tmp_dir_from_config, "dummy.csv")


def create_dummy_csv_batches(target_columns=None):
    if target_columns:
        df = pd.read_csv(
            os.path.join(tmp_dir_from_config, "dummy.csv"),
            converters={"bbox": convert_bbox},
            usecols=target_columns,
        )
    else:
        df = pd.read_csv(
            os.path.join(tmp_dir_from_config, "dummy.csv"),
            converters={"bbox": convert_bbox},
        )

    yield Batch(df)


def create_csv(num_rows, columns):
    csv_path = os.path.join(tmp_dir_from_config, "dummy.csv")
    try:
        os.remove(csv_path)
    except FileNotFoundError:
        pass
    df = pd.DataFrame(columns=columns)
    for col in columns:
        df[col] = np.random.randint(1, 100, num_rows)
    df.to_csv(csv_path, index=False)
    return df, csv_path


def create_text_csv(num_rows=30):
    """
    Creates a csv with 2 columns: id and comment
    The comment column has 2 values: "I like this" and "I don't like this" that are alternated
    """
    csv_path = os.path.join(tmp_dir_from_config, "dummy.csv")
    try:
        os.remove(csv_path)
    except FileNotFoundError:
        pass
    df = pd.DataFrame(columns=["id", "comment"])
    df["id"] = np.arange(num_rows)
    df["comment"] = np.where(df["id"] % 2 == 0, "I like this", "I don't like this")
    df.to_csv(csv_path, index=False)
    return csv_path


def create_table(table_name, num_rows, num_columns):
    # creates a table with num_rows tuples and columns = [a1, a2, a3, ...]
    columns = "".join("a{} INTEGER, ".format(i) for i in range(num_columns - 1))
    columns += "a{} INTEGER".format(num_columns - 1)
    create_table_query = "CREATE TABLE IF NOT EXISTS {} ( {} );".format(
        table_name, columns
    )
    execute_query_fetch_all(create_table_query)
    columns = ["a{}".format(i) for i in range(num_columns)]
    df, csv_file_path = create_csv(num_rows, columns)
    # load the CSV
    load_query = f"LOAD CSV '{csv_file_path}' INTO {table_name};"
    execute_query_fetch_all(load_query)
    df.columns = [f"{table_name}.{col}" for col in df.columns]
    return df


def create_sample_image():
    img_path = os.path.join(tmp_dir_from_config, "dummy.jpg")
    try:
        os.remove(img_path)
    except FileNotFoundError:
        pass

    img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
    img[0] -= 1
    img[2] += 1
    cv2.imwrite(img_path, img)
    return img_path


def create_sample_video(num_frames=NUM_FRAMES):
    file_name = os.path.join(tmp_dir_from_config, "dummy.avi")
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass

    duration = 1
    fps = NUM_FRAMES
    out = cv2.VideoWriter(
        file_name, cv2.VideoWriter_fourcc("M", "J", "P", "G"), fps, (32, 32), False
    )
    for i in range(fps * duration):
        data = np.array(np.ones((FRAME_SIZE[1], FRAME_SIZE[0])) * i, dtype=np.uint8)
        out.write(data)
    out.release()

    return os.path.join(tmp_dir_from_config, file_name)


def file_remove(path, parent_dir=tmp_dir_from_config):
    try:
        os.remove(os.path.join(parent_dir, path))
    except FileNotFoundError:
        pass


def create_dummy_batches(
    num_frames=NUM_FRAMES,
    filters=[],
    batch_size=10,
    start_id=0,
    video_dir=tmp_dir_from_config,
):
    if not filters:
        filters = range(num_frames)
    data = []
    for i in filters:
        data.append(
            {
                "myvideo.name": os.path.join(video_dir, "dummy.avi"),
                "myvideo.id": i + start_id,
                "myvideo.data": np.array(
                    np.ones((FRAME_SIZE[1], FRAME_SIZE[0], 3)) * i, dtype=np.uint8
                ),
                "myvideo.seconds": np.float32(i / num_frames),
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
            segment_data.append(np.ones((FRAME_SIZE[1], FRAME_SIZE[0], 3)) * i)
        segment_data = np.stack(np.array(segment_data, dtype=np.uint8))
        data.append(
            {
                "myvideo.name": "dummy.avi",
                "myvideo.id": segment[0] + start_id,
                "myvideo.data": segment_data,
                "myvideo.seconds": np.float32(i / num_frames),
            }
        )

        if len(data) % batch_size == 0:
            df = pd.DataFrame(data)
            df = df.astype({"myvideo.id": np.intp})
            yield Batch(df)
            data = []
    if data:
        df = pd.DataFrame(data)
        df = df.astype({"myvideo.id": np.intp})
        yield Batch(df)


def load_udfs_for_testing(mode="debug"):
    # DEBUG OR RELEASE MODE: ALL UDFs
    # MINIMAL MODE: NO YOLO
    init_builtin_udfs(mode=mode)


class DummyObjectDetector(AbstractClassifierUDF):
    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyObjectDetector"

    @property
    def labels(self):
        return ["__background__", "person", "bicycle"]

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["label"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        i = int(frames[0][0][0][0])
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
    def labels(self):
        return ["__background__", "person", "bicycle", "car"]

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["labels"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        i = int(frames[0][0][0][0])
        label = self.labels[i % 3 + 1]
        return np.array([label, label])


class DummyFeatureExtractor(AbstractClassifierUDF):
    """
    Returns a feature for a frame.
    """

    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyFeatureExtractor"

    @property
    def labels(self):
        return []

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        # Return the original input as its feature.

        def _extract_feature(row: pd.Series):
            feat_input = row[0]
            feat_input = feat_input.reshape(1, -1)
            feat_input = feat_input.astype(np.float32)
            return feat_input

        ret = pd.DataFrame()
        ret["features"] = df.apply(_extract_feature, axis=1)
        return ret


class DummyObjectDetectorDecorators(AbstractClassifierUDF):
    @decorators.setup(cachable=True, udf_type="object_detection", batchable=True)
    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyObjectDetectorDecorators"

    @property
    def labels(self):
        return ["__background__", "person", "bicycle"]

    @decorators.forward(
        input_signatures=[
            PandasDataframe(
                columns=["Frame_Array"],
                column_types=[NdArrayType.UINT8],
                column_shapes=[(3, 256, 256)],
            )
        ],
        output_signatures=[
            NumpyArray(
                name="label",
                type=NdArrayType.STR,
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["label"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        i = int(frames[0][0][0][0]) - 1
        label = self.labels[i % 2 + 1]
        return np.array([label])
