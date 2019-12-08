from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import VideoFormat, ColorSpace
from src.models.catalog.video_info import VideoMetaInfo
from src.models.storage.frame import Frame
from src.models.storage.batch import FrameBatch
from src.loaders.video_loader import SimpleVideoLoader
from src.loaders.abstract_loader import AbstractLoader

from os.path import split, dirname
import cv2
from typing import List, Tuple
from glob import glob
import numpy as np
import random
import os


class ActionClassificationLoader(AbstractLoader):
    def __init__(self, batchSize):
        self.batchSize = batchSize

    def load_images(self, dir: str):
        return None

    def load_labels(self, dir: str):
        return None

    def load_boxes(self, dir: str):
        return None

    def getLabelMap(self):
        return self.labelMap

    def findDataNames(self, searchDir):
        """
        findDataNames enumerates all training data for the model and 
        returns a list of tuples where the first element is a EVA VideoMetaInfo 
        object and the second is a string label of 
        the correct video classification

        Inputs:
         - searchDir = path to the directory containing the video data

        Outputs:
         - videoFileNameList = list of tuples where each tuple corresponds 
                               to a video in the data set. 
                               The tuple contains the path to the video,
                               its label, and a nest tuple containing the shape
         - labelList = a list of labels that correspond to labels in labelMap
         - inverseLabelMap = an inverse mapping between the string 
                             representation of the label name and an 
                             integer representation of that label
        """

        # Find all video files and corresponding labels in search directory
        videoFileNameList = glob(searchDir + "**/*.avi", recursive=True)
        random.shuffle(videoFileNameList)

        labels = [split(dirname(a))[1] for a in videoFileNameList]

        videoMetaList = [VideoMetaInfo(f, 30, VideoFormat.AVI) 
                         for f in videoFileNameList]

        inverseLabelMap = {k: v for (k, v) in enumerate(list(set(labels)))}

        labelMap = {v: k for (k, v) in enumerate(list(set(labels)))}
        labelList = [labelMap[l] for l in labels]

        return (videoMetaList, labelList, inverseLabelMap)

    def load_video(self, searchDir):

        print("load")

        self.path = searchDir
        (self.videoMetaList, 
         self.labelList, 
         self.labelMap) = self.findDataNames(self.path)
       
        videoMetaIndex = 0
        while videoMetaIndex < len(self.videoMetaList):

            # Get a single batch
            frames = []
            labels = np.zeros((0, 51))
            while len(frames) < self.batchSize:

                # Load a single video
                meta = self.videoMetaList[videoMetaIndex]
                videoFrames, info = self.loadVideo(meta)
                videoLabels = np.zeros((len(videoFrames), 51))
                videoLabels[:, self.labelList[videoMetaIndex]] = 1
                videoMetaIndex += 1
                    
                # Skip unsupported frame types
                if info != FrameInfo(240, 320, 3, ColorSpace.RGB): 
                    continue

                # Append onto frames and labels
                frames += videoFrames
                labels = np.append(labels, videoLabels, axis=0)

            yield FrameBatch(frames, info), labels

    def loadVideo(self, meta):
        video = cv2.VideoCapture(meta.file)
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        _, frame = video.read()
        frame_ind = 0

        info = None
        if frame is not None:
            (height, width, channels) = frame.shape
            info = FrameInfo(height, width, channels, ColorSpace.RGB)

        frames = []
        while frame is not None:
            # Save frame
            eva_frame = Frame(frame_ind, frame, info)
            frames.append(eva_frame)
            
            # Read next frame
            _, frame = video.read()
            frame_ind += 1

        return (frames, info)