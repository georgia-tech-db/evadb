import cv2
import numpy as np

"""

Utility functions to calculate inter-frame difference

"""

class DistanceMetrics:
	def convert_to_grayscale(self, frame):
		return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	def absolute_difference(self, curr_frame, prev_frame):
		curr_frame_grayscale = self.convert_to_grayscale(curr_frame)
		prev_frame_grayscale = self.convert_to_grayscale(prev_frame)
		frame_diff = cv2.absdiff(curr_frame_grayscale, prev_frame_grayscale)
		return frame_diff.sum()

	def mse_difference(self, curr_frame, prev_frame):
		curr_frame_grayscale = self.convert_to_grayscale(curr_frame)
		prev_frame_grayscale = self.convert_to_grayscale(prev_frame)
		total_pixels = curr_frame_grayscale.shape[0]*curr_frame_grayscale.shape[1]
		frame_diff = curr_frame_grayscale.astype('float') - prev_frame_grayscale
		mse_diff = np.sum(frame_diff**2)/float(total_pixels)
		return mse_diff

def frame_difference(curr_frame, prev_frame, distance_metric):
	distance_metrics = DistanceMetrics()
	diff = getattr(distance_metrics, distance_metric)
	frame_diff = diff(curr_frame, prev_frame)
	return frame_diff

def compare_foreground_mask(curr_frame, prev_frame, distance_metric):
	curr_foreground = curr_frame
	prev_foreground = prev_frame
	return frame_difference(curr_foreground, prev_foreground, distance_metric)

