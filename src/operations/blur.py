import cv2


class Blur:
	def __init__(self, kernel_size=5):
		self.id = None
		self.kernel_size = kernel_size
		pass

	def apply(self, frames):
		for frame in frames:
			blur = cv2.blur(frame.image, (self.kernel_size, self.kernel_size))
			frame.image = blur
		return frames
