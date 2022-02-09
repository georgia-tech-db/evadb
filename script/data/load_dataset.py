import cv2
import json
import os
import sys
from tqdm import tqdm

import numpy as np
import nest_asyncio
import pandas as pd

# eva lib
sys.path.insert(0,'./../')
from eva.server.db_api import connect

# establish connection to eva db
nest_asyncio.apply()
connection = connect(host = '0.0.0.0', port = 5432) # hostname, port of the server where EVADB is running
cursor = connection.cursor()

# utility functions
def convert_json_to_csv(dataset_name, info_path, start_index, video_id, total_frames, dump=False):
    """
    Parses a given info json file into a csv and dumps it (optionally). 
    total_frames is required to know which entry in the json corresponds to which frame id of video
    
    Args:
        dataset_name (string) - name of the dataset this video belongs to. There should be table existing with this name
        info_path (string) - path to the info file
        start_index (int) - starting index for this csv
        video_id (int) - video id
        total_frames (int) - total frames of the current video
        dump (bool) - dumps the dataframe as a csv in the same destination
    """
    
    print(f"info_path: {info_path} total_frame: {total_frames} start_index: {start_index} video_id: {video_id}")
    info_file_name = info_path.split('/')[-1].split('.')[0]
    info_folder_path = "/".join(info_path.split('/')[:-1])
    
    if os.path.exists(os.path.join(info_folder_path, info_file_name + ".csv")):
        print(f"already converted to csv")
        return
        
    with open(info_path, 'rb') as json_file:
        info_json = json.load(json_file)
        
    # number of frames for which we have information
    num_frames_info = len(info_json)
    
    # we assume the entries in the frame info are equally spaced
    # eg: if there are 100 total frames and 10 entries in info_json, then sample_frequency = 10 or we have info for 
    # every 10 frames
    sample_frequency = total_frames / num_frames_info
    
    meta = {}
    i = start_index
    
    for info in info_json:
        frame_index = int(info['frameIndex'])
        frame_id = int(frame_index * sample_frequency)

        for label in info['labels']:
            object_label = label['category']
            #bbox = np.array([[label['box2d']['x1'], label['box2d']['y1']], [label['box2d']['x2'], label['box2d']['y2']]])
            bbox = f"{label['box2d']['x1']}, {label['box2d']['y1']}, {label['box2d']['x2']}, {label['box2d']['y2']}"
            object_id = int(label['id'])
            
            meta[i] = {
                "id" : i,
                "frame_id" : int(frame_id),
                "video_id" : int(video_id),
                "dataset_name" : dataset_name,
                "label" : object_label,
                "bbox" : bbox,
                "object_id" : object_id
            }
            i += 1
                
    meta_df = pd.DataFrame.from_dict(meta, "index")
    
    if dump:
        print(f"dumping in {info_folder_path}")
        meta_df.to_csv(os.path.join(info_folder_path, info_file_name + ".csv"), index=False)
        
    return i, meta_df


def convert_all_meta_to_csv(dataset_name):
    """
    Looks at the info folder of the given dataset. Converts each one of the json file into a csv file (in the required format)
    and dumps it in the same folder. Currently supports only the format of BDD
    
    Args:
        dataset_name (string) - name of given dataset
    """
    
    # root folder path
    eva_root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
    #eva_root_folder = "../"

    # dataset_name must be your folder name
    dataset_path = os.path.join(eva_root_folder, 'data', 'datasets', dataset_name)
    print(f"Loading {dataset_name} from the path {dataset_path}")

    # videos contains the raw videos
    videos_path = os.path.join(dataset_path, 'videos')

    # info contains a json file corresponding to each video
    info_path = os.path.join(dataset_path, 'info')

    # Load the paths for all videos and info files
    video_files = [os.path.join(videos_path, f) for f in sorted(os.listdir(videos_path))]
    info_files = [os.path.join(info_path, f) for f in sorted(os.listdir(info_path))]
    
    # since we dont have support for auto_increment, manually adding an index column
    index = 0
    
    # convert each one of the meta json file to csv
    dataset_len = len(video_files)
    for i in range(dataset_len):
        # total frames is required to map the frame id correctly
        total_frames = cv2.VideoCapture(video_files[i]).get(7)
        new_index, df = convert_json_to_csv(dataset_name, info_files[i], start_index=index, video_id=i, total_frames=total_frames, dump=True)
        index = new_index
        
    return df

def create_meta_table(dataset_name):
    """
    Creates a meta table for the given dataset
    TODO: Make this function more flexible to receive column name, type etc..
    
    Args:
        dataset_name (string) - name of dataset
        
    Returns:
        True/False depending on if table creation was successful or not.
    """
    
    table_name = dataset_name + "meta"
    
    # Make this query dynamic later
    '''
    create_table_query = f""" 

    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER UNIQUE,
        frame_id INTEGER,
        video_id INTEGER,
        labels NDARRAY STR(ANYDIM),
        bboxes NDARRAY FLOAT32(ANYDIM, 4),
        object_ids NDARRAY FLOAT32(ANYDIM)
    );
    """
    '''
    create_table_query = f""" 

    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER UNIQUE,
        frame_id INTEGER,
        video_id INTEGER,
        dataset_name TEXT(30),
        label TEXT(30),
        bbox NDARRAY FLOAT32(4),
        object_id INTEGER
    );
    """
    
    cursor.execute(create_table_query)
    response = cursor.fetch_all()
    
    if response.status == '0':
        return True
    else:
        return False

def load_video(dataset_name, video_path, info_path):
    """
    Takes the path to 1 video and its corresponding json file. 
    Iterates over each frame of the video and performs an INSERT operation on the table
    
    Args:
        dataset_name (string) - name of the dataset this video belongs to. There should be table existing with this name
        video_path (string) - path of the video to be loaded
        info_path (string) - path of the json file that contains info about the video
    """
    
    table_name = dataset_name + "meta"
    print(f"Loading video from: {video_path} info from: {info_path} into {table_name}")
    
    # load meta
    meta_name_with_ext = info_path.split('/')[-1]
    meta_name = meta_name_with_ext.split('.')[0]
    upload_meta_query = f'UPLOAD INFILE "{info_path}" PATH "{meta_name_with_ext}";'
    load_meta_query = f'LOAD DATA INFILE "{meta_name_with_ext}" INTO {table_name};'
    
    print(f"upload_meta_query: {upload_meta_query}")
    print(f"load_meta_query: {load_meta_query}")
    
    cursor.execute(upload_meta_query)
    response = cursor.fetch_all()
    print(f"response from upload query: {response}")
    
    cursor.execute(load_meta_query)
    response = cursor.fetch_all()
    print(f"response from load query: {response}")
    
    if int(response.status) != 0:
        return False
    
    # load video
    video_name_with_ext = video_path.split('/')[-1]
    video_name = video_name_with_ext.split('.')[0]
    upload_video_query = f'UPLOAD INFILE "{video_path}" PATH "{video_name_with_ext}";'
    load_video_query = f'LOAD DATA INFILE "{video_name_with_ext}" INTO {video_name};'
    
    print(f"upload_video_query: {upload_video_query}")
    print(f"load_video_query: {load_video_query}")
    
    cursor.execute(upload_video_query)
    response = cursor.fetch_all()
    print(f"response from upload query: {response}")
    
    cursor.execute(load_video_query)
    response = cursor.fetch_all()
    print(f"response from load query: {response}")
    
    return True

def load_dataset(dataset_name):
    """
    A folder named dataset_name is expected to be inside datasets. This folder should contain 2 other folders named info and videos
    
    Args:
        dataset_name (string) - name of the dataset
        
    Returns:
        True if all videos have been loaded succesfully
        False if there was any error
    """
        
    # root folder path
    home_folder = os.path.expanduser('~')
    eva_root_folder = os.path.join(home_folder, '.eva')

    # dataset_name must be your folder name
    dataset_path = os.path.join(eva_root_folder, 'data', 'datasets', dataset_name)
    print(f"Loading {dataset_name} from the path {dataset_path}")

    # first create a meta table for this dataset if it doesnt exist
    if create_meta_table(dataset_name):
        print(f"Table created successfully for {dataset_name} (or already exists)")
    else:
        return False

    # Load the paths for all videos and info files
    videos_path = os.path.join(dataset_path, 'videos')
    info_path = os.path.join(dataset_path, 'info')
    video_files = [os.path.join(videos_path, f) for f in sorted(os.listdir(videos_path))]
    info_files = [os.path.join(info_path, f) for f in sorted(os.listdir(info_path))]
    
    # check that each video under videos has a corresponding meta file
    for video_file in video_files:
        video_name = video_file.split('/')[-1].split('.')[-2]
        expected_info_file = os.path.join(dataset_path, 'info', video_name + '.csv')
        if expected_info_file not in info_files:
            print(f"Each video under videos should have a corresponding info file under info.")
            return False
            
    # loop through each video and load them one by one
    dataset_len = len(video_files)
    for video_index in tqdm(range(dataset_len)):
        video_path = video_files[video_index]
        info_path = info_files[video_index]
        
        # load this video along with its meta info
        if not load_video(dataset_name, video_path, info_path):
            return False
        
    return True


if __name__ == "__main__":
    
    # fetch the dataset name from the command line
    dataset_name = sys.argv[1]

    # load the dataset
    if load_dataset(dataset_name):
        print(f"Dataset loaded successfully!")
    else:
        print(f"One or more video loads failed! ")