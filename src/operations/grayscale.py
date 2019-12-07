import cv2
import numpy as np


class Grayscale:

	def __init__(self):
		self.id = None

	def apply(self, frames):
		for frame in frames:
			gray2d = cv2.cvtColor(frame.image, cv2.COLOR_BGR2GRAY)
			gray_im = np.repeat(gray2d[:, :, None], 3, axis=2)
			frame.image = gray_im
		return frames
