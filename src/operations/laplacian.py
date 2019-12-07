import cv2

class Laplacian:
	def __init__(self):
		self.id = None
		pass

	def apply(self, frames):
		for frame in frames:
			laplacian = cv2.Laplacian(frame.image,cv2.CV_64F)
			frame.image = laplacian
		return frames
