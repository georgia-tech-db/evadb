from src.models import FrameBatch, Prediction, FrameInfo, Point, BoundingBox, ColorSpace, VideoMetaInfo, VideoFormat
from src.loaders.video_loader import SimpleVideoLoader
from src.udfs.abstract_udfs import AbstractClassifierUDF

#from keras.models import Sequential
#from keras.layers import Dense, Conv2D, Flatten

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Conv2D, Flatten

from typing import List, Tuple
from glob import glob
import numpy as np
import random
import os

class VideoToFrameClassifier(AbstractClassifierUDF):

    def __init__(self):
        # Build the model
        self.model = self.buildModel()

        # Get dataset directory and stored data
        dataset = "./data/hmdb/"
        videoMetaList, labelList, self.inverseLabelMap = self.findDataNames(dataset)

        # Train the model using shuffled data
        self.trainModel(self.model, videoMetaList, labelList, 10)

    def findDataNames(self, searchDir):
        """
        findDataNames enumerates all training data for the model and 
        returns a list of tuples where the first element is a EVA VideoMetaInfo 
        object and the second is a string label of the correct video classification

        Inputs:
         - searchDir = path to the directory containing the video data

        Outputs:
         - videoFileNameList = list of tuples where each tuple corresponds to a video
                               in the data set. The tuple contains the path to the video,
                               its label, and a nest tuple containing the shape
         - labelList = a list of labels that correspond to the labels in labelMap
         - inverseLabelMap = an inverse mapping between the string representation of the label
                             name and an integer representation of that label

        """

        # Find all video files and corresponding labels in search directory
        videoFileNameList = glob(searchDir+"**/*.avi", recursive=True)
        random.shuffle(videoFileNameList)

        labels = [os.path.split(os.path.dirname(a))[1] for a in videoFileNameList]

        videoMetaList = [VideoMetaInfo(f,30,VideoFormat.AVI) for f in videoFileNameList]
        inverseLabelMap = {k:v for (k,v) in enumerate(list(set(labels)))}

        labelMap = {v:k for (k,v) in enumerate(list(set(labels)))}
        labelList = [labelMap[l] for l in labels]

        return (videoMetaList, labelList, inverseLabelMap)

    def trainModel(self, model, videoMetaList, labelList, n = 10):
        """
        trainModel trains the built model using chunks of data of size n videos

        Inputs:
         - model = model object to be trained
         - videoMetaList = list of tuples where the first element is a EVA VideoMetaInfo 
                           object and the second is a string label of the 
                           correct video classification
         - labelList = list of labels derived from the labelMap
         - n = integer value for how many videos to act on at a time
        """

        labelArray = np.array(labelList)

        for i,videoInfo in enumerate(videoMetaList):
            # Load the video from disk into memory
            videoLoader = SimpleVideoLoader(videoInfo)
            batches = videoLoader.load()

            for b in batches:
                # Get the frames as a numpy array
                frames = b.frames_as_numpy_array()

                # Skip unsupported frame sizes
                if frames.shape[1:] != (240, 320, 3):
                    break

                labels = np.zeros((frames.shape[0],51))
                labels[:,labelList[i]] = 1

                print(frames.shape)
                print(labels.shape)

                # Split x and y into training and validation sets
                xTrain = frames[0:int(0.8*frames.shape[0])]
                yTrain = labels[0:int(0.8*labels.shape[0])]

                xTest = frames[int(0.8*frames.shape[0]):]
                yTest = labels[int(0.8*labels.shape[0]):]

                print(xTrain)
                print(yTrain)

                # Train the model using cross-validation (so we don't need to explicitly do CV outside of training)
                model.fit(xTrain, yTrain, validation_data = (xTest, yTest), epochs = 2)            

    def buildModel(self):
        """
        buildModel sets up a convolutional 2D network using a reLu activation function

        Outputs:
         - model = model object to be used later for training and classification
        """
        # We need to incrementally train the model so we'll set it up before preparing the data
        model = Sequential()

        # Add layers to the model
        model.add(Conv2D(64, kernel_size = 3, activation = "relu", input_shape=(240, 320, 3)))
        model.add(Conv2D(32, kernel_size = 3, activation = "relu"))
        model.add(Flatten())
        model.add(Dense(51, activation = "softmax"))

        # Compile model and use accuracy to measure performance
        model.compile(optimizer = "adam", loss = "categorical_crossentropy", metrics = ["accuracy"])

        return model

    def input_format(self) -> FrameInfo:
        return FrameInfo(240, 320, 3, ColorSpace.RGB)

    @property
    def name(self) -> str:
        return "Paula_Test_Funk"

    def labels(self) -> List[str]:
        return [
        'brush_hair', 'clap', 'draw_sword', 'fall_floor', 'handstand', 'kick', 'pick', 'push', 'run', 
        'shoot_gun', 'smoke', 'sword', 'turn', 'cartwheel', 'climb', 'dribble', 'fencing', 'hit', 
        'kick_ball', 'pour', 'pushup', 'shake_hands', 'sit', 'somersault', 'sword_exercise', 'walk', 'catch', 
        'climb_stairs', 'drink', 'flic_flac', 'hug', 'kiss', 'pullup', 'ride_bike', 'shoot_ball', 'situp', 
        'stand', 'talk', 'wave', 'chew', 'dive', 'eat', 'golf', 'jump', 'laugh', 'punch', 'ride_horse', 
        'shoot_bow', 'smile', 'swing_baseball', 'throw', 
        ]

    def classify(self, batch: FrameBatch) -> List[Prediction]:
        """
        Takes as input a batch of frames and returns the predictions by applying the classification model.

        Arguments:
            batch (FrameBatch): Input batch of frames on which prediction needs to be made

        Returns:
            List[Prediction]: The predictions made by the classifier
        """
        
        pred = model.predict(batch.frames_as_numpy_array())
        return [self.inverseLabelMap[l] for l in pred]
