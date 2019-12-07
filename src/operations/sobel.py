import cv2


class SobelX:
    def __init__(self, kernel_size=5):
        self.id = None
        self.kernel_size = kernel_size
        pass

    def apply(self, frames):
        for frame in frames:
            sobelx = cv2.Sobel(frame.image,cv2.CV_64F, 1, 0, self.kernel_size)
            frame.image = sobelx
        return frames

class SobelY:
    def __init__(self, kernel_size=5):
        self.id = None
        self.kernel_size = kernel_size
        pass

    def apply(self, frames):
        for frame in frames:
            sobely = cv2.Sobel(frame.image,cv2.CV_64F, 0, 1, self.kernel_size)
            frame.image = sobely
        return frames
