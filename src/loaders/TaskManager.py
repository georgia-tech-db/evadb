# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from .color_detection import process_image
from .intersection_detection import intersection_detector


class TaskManager():

    def __init__(self):
        self.images = None
        self.img_bboxes = None

    def call_color(self, image, img_bboxes):
        colors = []
        for bbox in img_bboxes:
            top = bbox[0]
            left = bbox[1]
            bottom = bbox[2]
            right = bbox[3]
            # image is already going to be an array

            img_to_pass = image[top:bottom, left:right, :]
            """
            if __debug__:
                print("inside task manager img shape is " + str(
                img_to_pass.shape))
                print("   original image shape is " + str(image.shape))
                print("   original image type is " + str(type(image)))
                print("(left, top, right, bottom coords are " + str((left,
                top, right, bottom)))
            """
            color = process_image(img_to_pass).lower()
            if color != "":
                colors.append(color)
            else:
                colors.append(None)

        return colors

    def call_intersection(self, image, scene, img_bboxes):

        return intersection_detector(image, scene, img_bboxes)
