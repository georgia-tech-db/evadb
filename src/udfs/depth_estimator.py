from typing import List, Tuple

import numpy as np
import torchvision
import sys
import os
import torch
import cv2

from src.model import net
from src.udfs.abstract_udfs import AbstractClassifierUDF
from src.models import FrameBatch, Prediction, FrameInfo, Point, BoundingBox, ColorSpace
from torch.autograd import Variable
from torchvision import transforms
from src.depth_estimation_result import DepthEstimationResult

sys.path.append('../')
sys.path.append('.')
folder = os.path.dirname(os.path.abspath(__file__))

CMAP = np.load(os.path.join(folder, 'cmap_kitti.npy'))
IMG_SCALE = 1. / 255
IMG_MEAN = np.array([0.485, 0.456, 0.406]).reshape((1, 1, 3))
IMG_STD = np.array([0.229, 0.224, 0.225]).reshape((1, 1, 3))
HAS_CUDA = torch.cuda.is_available()
NUM_CLASSES = 6
NUM_TASKS = 2  # segm + depth

class DepthEstimator(AbstractClassifierUDF):
    """

    UDF class for depth estimation feature. responsible for taking batch of frames.
    It processes the frames, sends them to deep learning model for predictions.
    Consolidates the model output and store them in DepthEstimationResult object.
    Arguments:
        Takes AbstractClassifierUDF as input since it implements the abstract UDF class.

    """

    @property
    def name(self) -> str:
        return "Net"

    def __init__(self):
        super().__init__()
        self.model = net(num_classes=NUM_CLASSES, num_tasks=NUM_TASKS)
        if HAS_CUDA:
            _ = self.model.cuda()
            _ = self.model.eval()
        ckpt = torch.load(os.path.join(folder, 'ExpKITTI_joint.ckpt'))
        self.model.load_state_dict(ckpt['state_dict'])

    @property
    def input_format(self) -> FrameInfo:
        return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    @property
    def labels(self) -> List[str]:
        return [
        ]

    def classify(self, batch: FrameBatch) -> List[Prediction]:
        pass

    # subtract the mean and remove the noise from the image
    def prepare_img(self, img):
        return (img * IMG_SCALE - IMG_MEAN) / IMG_STD

    def _get_depth_estimation(self, frames: np.ndarray) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Performs depth and segmentation predictions on input frames
        Arguments:
            frames (np.ndarray): Frames on which predictions need to be performed

        Returns:
            tuple containing predicted_segments (List[List[float]]), predicted_depths (List[List[float]])

        """

        depths = []
        segms = []

        # process frames in a loop
        for img in frames:
            # create tensor from numpy for each image
            img_var = Variable(torch.from_numpy(self.prepare_img(img).transpose(2, 0, 1)[None]),
                               requires_grad=False).float()
            if HAS_CUDA:
                img_var = img_var.cuda()

            # pass image to deep learning model for prediction
            segm, depth = self.model(img_var)

            # resize the segmentation and depth arrays
            segm = cv2.resize(segm[0, :NUM_CLASSES].cpu().data.numpy().transpose(1, 2, 0),
                              img.shape[:2][::-1],
                              interpolation=cv2.INTER_CUBIC)
            depth = cv2.resize(depth[0, 0].cpu().data.numpy(),
                               img.shape[:2][::-1],
                               interpolation=cv2.INTER_CUBIC)
            depth = np.abs(depth)
            depths.append(depth)
            segms.append(segm)

        return segms, depths

    def process_frames(self, batch: FrameBatch) -> List[DepthEstimationResult]:
        """
                sends input frames to utility method for prediction and then returns the result in DepthEstimationResult object.
                Arguments:
                    FrameBatch (np.ndarray): Batch of Frames on which predictions need to be performed

                Returns:
                    list of DepthEstimationResult object where each object contains [frame, depth, segmentation] value.

        """

        frames = batch.frames_as_numpy_array()

        # call depth estimation on batch frames
        (segms, depths) = self._get_depth_estimation(frames)

        #process the model output and store it in DepthEstimationResult object
        return DepthEstimationResult.depth_estimation_result_from_batch_and_lists(batch, segms, depths)

