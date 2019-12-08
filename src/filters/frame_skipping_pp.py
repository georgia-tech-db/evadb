from src.filters.abstract_pp import AbstractPP
from src.utils import image_utils
from typing import List


class frameSkippingPP(AbstractPP):
    """
    Class that performs the task of frame skipping. 
    Frame skipping can be done in two ways:
        1. Compare all pixels of a frame
        2. Compare only foreground pixels.
    """
    def __init__(self, threshold=0.0, compare_foreground=False, 
                 distance_metric='absolute_difference'):
        """
        Constructor for this class.

        :param threshold: threshold value below which frames are skipped
        :param compare_foreground: boolean value to indicate if only 
                                   foreground objects are to be compared.
        :param distance_metric: the distance metric to be used for 
                                frame comparison
        :return None
        """        
        self.threshold = threshold
        self.compare_foreground = compare_foreground
        self.distance_metric = distance_metric

    def predict(self, batch) -> List[bool]:
        """
        Function that predicts whether a frame needs to be skipped or not
        based on the threshold value set.

        :param batch: an EVA batch of frames
        :return List of booleans that indicates whether the frame at a given
                index should be skipped or not.
                True => skip frame
                False => do not skip frame
        """
        prev_frame = None
        skipFrames = []
        frames = batch.frames_as_numpy_array()
        for frame in frames:
            if prev_frame is not None:
                """
                If compare_foreground set to true, calculate distance
                metric on only the foreground pixels
                else on the entire image.
                """
                if self.compare_foreground is True:
                    frame_diff = self.compare_foreground_mask(
                        frame, prev_frame, self.distance_metric)
                else: 
                    frame_diff = self.frame_difference(
                        frame, prev_frame, self.distance_metric)
                if frame_diff < self.threshold:
                    skipFrames.append(True)
                else:
                    skipFrames.append(False)
                    prev_frame = frame
            else:
                skipFrames.append(False)
                prev_frame = frame
        return skipFrames

    def frame_difference(self, curr_frame, prev_frame, distance_metric):
        """
        Function to calculate frame difference based on distance metric
        
        :param curr_frame: current frame to be processed from a batch
        :param prev_frame: previous frame with difference > threshold
        :param distance_metric: the distance metric to be used for 
                                frame comparison
        :return difference value of the two frames
        """
        diff = getattr(image_utils, distance_metric)
        frame_diff = diff(curr_frame, prev_frame)
        return frame_diff

    def compare_foreground_mask(self, curr_frame, prev_frame, distance_metric):
        """
        Function to calculate difference of two frames. Compares only the
        difference between the foreground objects. Obtains the foregound 
        objects and then calculates the frame difference

        :param curr_frame: current frame to be processed from a batch
        :param prev_frame: previous frame with difference > threshold
        :param distance_metric: the distance metric to be used for 
                                frame comparison
        :return difference value of the two frames
        """
        curr_foreground = mask_background(curr_frame)
        prev_foreground = mask_background(prev_frame)
        return frame_difference(curr_foreground, prev_foreground, distance_metric)