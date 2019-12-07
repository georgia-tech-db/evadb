import cv2


class ScharrX:
    def __init__(self):
        self.id = None
        pass

    def apply(self, frames):
        for frame in frames:
            scharrx = cv2.Scharr(frame.image,cv2.CV_64F, 1, 0)
            frame.image = scharrx
        return frames

class ScharrY:
    def __init__(self):
        self.id = None
        pass

    def apply(self, frames):
        for frame in frames:
            scharry = cv2.Scharr(frame.image,cv2.CV_64F, 0, 1)
            frame.image = scharry
        return frames
