from filters.color_detection import process_image
from filters.intersection_detection import intersection_detector

import numpy as np
class TaskManager():

    def __init__(self,images,img_bbox,img_class,task="color"):
        self.images=images
        self.img_bbox=img_bbox
        self.img_class=img_class
        if task=='color':
            self.call_color()
        elif task=='speed':
            self.call_speed()
        elif task=='intersection':
            self.call_intersection()

    def call_color(self):
        color = []
        print(len(self.images))
        for cnt,img in enumerate(self.images):
            for bbox in self.img_bbox[cnt]:
                img_to_pass =np.asarray(img[bbox[1]:bbox[3],bbox[0]:bbox[2]])
                print(img_to_pass.shape)
                color.append(process_image(img_to_pass))
        print(color)
        return color

    def call_speed(self):
        pass

    def call_intersection(self):
        intersection=[]
        for cnt,img in enumerate(self.images):
            intersection.append(intersection_detector(img,'MVI_20011',self.img_bbox))
        return color
        