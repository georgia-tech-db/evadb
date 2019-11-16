import cv2

"""

Utility functions to calculate inter-frame difference

"""

def convert_to_grayscale(self, frame):
	return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def absolute_difference(self, curr_frame, prev_frame):
	curr_frame_grayscale = convert_to_grayscale(curr_frame)
	prev_frame_grayscale = convert_to_grayscale(prev_frame)
	frame_diff = cv2.absdiff(curr_frame_grayscale, prev_frame_grayscale)
	return frame_diff