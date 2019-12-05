import numpy as np
import cv2


def convert_to_grayscale(self, frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def absolute_difference(self, curr_frame, prev_frame):
    curr_frame_grayscale = self.convert_to_grayscale(curr_frame)
    prev_frame_grayscale = self.convert_to_grayscale(prev_frame)
    frame_diff = cv2.absdiff(curr_frame_grayscale, prev_frame_grayscale)
    return frame_diff.sum()


def mse_difference(self, curr_frame, prev_frame):
    curr_frame_gray = self.convert_to_grayscale(curr_frame)
    prev_frame_gray = self.convert_to_grayscale(prev_frame)
    total_pixels = curr_frame_gray.shape[0] * curr_frame_gray.shape[1]
    frame_diff = curr_frame_gray.astype('float') - prev_frame_gray
    mse_diff = np.sum(frame_diff**2) / float(total_pixels)
    return mse_diff
