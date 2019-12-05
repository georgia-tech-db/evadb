import cv2
import os
import argparse
from write_frames import write_frames




parser = argparse.ArgumentParser(description='Arguments for Eva Storage')
    
parser.add_argument('-path_to',action='store',required = True,dest ='path_to',
                    help='Add path to folder')
    
parser.add_argument('-path_from',action='store',required = True,dest ='path_from',
                    help='Add path from video')
args = parser.parse_args()

path_to = args.path_to
path_from = args.path_from
    
write_frames(path_from, path_to)