import cv2
import numpy as np


class Grayscale:

    def __init__(self):
        pass

    @staticmethod
    def convert(images):
        images = list(images)
        gray_images = []
        for image in images:
            gray_images.append(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        return np.array(gray_images)
