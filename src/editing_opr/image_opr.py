import cv2
import numpy as np


class ImageOperations:

    def __init__(self):
        pass

    @staticmethod
    def grayscale(images):
        gray_images = []
        for image in images:
            gray2d = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_im = np.repeat(gray2d[:, :, None], 3, axis=2)
            gray_images.append(gray_im)
        return gray_images

    @staticmethod
    def blur(images, kernel_size):
        blurred_images = []
        for image in images:
            blur = cv2.blur(image, (kernel_size, kernel_size))
            blurred_images.append(blur)
        return blurred_images
