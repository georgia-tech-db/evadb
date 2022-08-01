import numpy as np
import pandas as pd
import cv2
import os
import shutil

from eva.models.storage.batch import Batch
from eva.models.catalog.frame_info import FrameInfo
from eva.models.catalog.properties import ColorSpace
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.abstract_udfs import AbstractClassifierUDF
from eva.udfs.udf_bootstrap_queries import init_builtin_udfs
from eva.configuration.configuration_manager import ConfigurationManager


NUM_FRAMES = 10
FRAME_SIZE = 2 * 2 * 3
CONFIG = ConfigurationManager()
PATH_PREFIX = CONFIG.get_value('storage', 'path_prefix')


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
        os.remove(os.path.join(PATH_PREFIX, 'dummy.csv'))
    except FileNotFoundError:
        pass

    sample_meta = {}

    index = 0
    sample_labels = ['car', 'pedestrian', 'bicycle']
    num_videos = 2
    for video_id in range(num_videos):
        for frame_id in range(num_frames):
            random_coords = 200 + 300 * np.random.random(4)
            sample_meta[index] = {
                'id': index,
                'frame_id': frame_id,
                'video_id': video_id,
                'dataset_name': 'test_dataset',
                'label': sample_labels[np.random.choice(len(sample_labels))],
                'bbox': ",".join([str(coord) for coord in random_coords]),
                'object_id': np.random.choice(3)
            }

            index += 1

    df_sample_meta = pd.DataFrame.from_dict(sample_meta, "index")
    df_sample_meta.to_csv(os.path.join(PATH_PREFIX, 'dummy.csv'),
                          index=False)


def create_dummy_csv_batches():
    df = pd.read_csv(os.path.join(PATH_PREFIX, 'dummy.csv'),
                     converters={'bbox': convert_bbox})
    return Batch(df)


def create_csv(num_rows, columns):
    try:
        os.remove(os.path.join(PATH_PREFIX, 'dummy.csv'))
    except FileNotFoundError:
        pass
    df = pd.DataFrame(columns=columns)
    for col in columns:
        df[col] = np.random.randint(1, 100, num_rows)
    df.to_csv(os.path.join(PATH_PREFIX, 'dummy.csv'),
              index=False)
    return df


def create_table(table_name, num_rows, num_columns):
    # creates a table with num_rows tuples and columns = [a1, a2, a3, ...]
    columns = ''.join('a{} INTEGER, '.format(i)
                      for i in range(num_columns - 1))
    columns += 'a{} INTEGER'.format(num_columns - 1)
    create_table_query = 'CREATE TABLE IF NOT EXISTS {} ( {} );'.format(
        table_name, columns)
    execute_query_fetch_all(create_table_query)
    columns = ['a{}'.format(i) for i in range(num_columns)]
    df = create_csv(num_rows, columns)
    # load the CSV
    load_query = """LOAD DATA INFILE 'dummy.csv' INTO {}
                   WITH FORMAT CSV;""".format(table_name)
    execute_query_fetch_all(load_query)
    df.columns = [f'{table_name}.{col}' for col in df.columns]
    return df


def create_sample_video(num_frames=NUM_FRAMES):
    try:
        os.remove(os.path.join(PATH_PREFIX, 'dummy.avi'))
    except FileNotFoundError:
        pass

    out = cv2.VideoWriter(os.path.join(PATH_PREFIX, 'dummy.avi'),
                          cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
                          (2, 2))
    for i in range(num_frames):
        frame = np.array(np.ones((2, 2, 3)) * float(i + 1) * 25,
                         dtype=np.uint8)
        out.write(frame)


def copy_sample_video_to_prefix():
    shutil.copyfile('data/ua_detrac/ua_detrac.mp4',
                    os.path.join(PATH_PREFIX, 'ua_detrac.mp4'))


def file_remove(path):
    os.remove(os.path.join(PATH_PREFIX, path))


def create_dummy_batches(num_frames=NUM_FRAMES,
                         filters=[], batch_size=10, start_id=0):
    if not filters:
        filters = range(num_frames)
    data = []
    for i in filters:
        data.append({'myvideo.id': i + start_id,
                     'myvideo.data': np.array(
                         np.ones((2, 2, 3)) * float(i + 1) * 25,
                         dtype=np.uint8)})

        if len(data) % batch_size == 0:
            yield Batch(pd.DataFrame(data))
            data = []
    if data:
        yield Batch(pd.DataFrame(data))


def load_inbuilt_udfs():
    mode = ConfigurationManager().get_value('core', 'mode')
    init_builtin_udfs(mode=mode)


class DummyObjectDetector(AbstractClassifierUDF):

    @property
    def name(self) -> str:
        return "DummyObjectDetector"

    def __init__(self):
        super().__init__()

    @property
    def input_format(self):
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self):
        return ['__background__', 'person', 'bicycle']

    def classify(self, df: pd.DataFrame):
        ret = pd.DataFrame()
        ret['label'] = df.apply(self.classify_one, axis=1)
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
    @property
    def name(self) -> str:
        return "DummyMultiObjectDetector"

    def __init__(self):
        super().__init__()

    @property
    def input_format(self):
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self):
        return ['__background__', 'person', 'bicycle', 'car']

    def classify(self, df: pd.DataFrame):
        ret = pd.DataFrame()
        ret['labels'] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        i = int(frames[0][0][0][0] * 25) - 1
        label = self.labels[i % 3 + 1]
        return np.array([label, label])
