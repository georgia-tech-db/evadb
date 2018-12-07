from loaders.color_detection import process_image
from loaders.intersection_detection import intersection_detector
import time
import numpy as np



class TaskManager():

    def __init__(self):
        self.images = None
        self.img_bboxes = None

    def call_color(self, image, img_bboxes):
        colors = []
        for bbox in img_bboxes:
            left = bbox[0]
            top = bbox[1]
            right = bbox[2]
            bottom = bbox[3]
            #image is already going to be an array
            img_to_pass = image[top:bottom][left:right]
            colors.append(process_image(img_to_pass))
        return colors


    def call_intersection(self, image, img_bboxes):

        return intersection_detector(image, 'MVI_20011', img_bboxes)

