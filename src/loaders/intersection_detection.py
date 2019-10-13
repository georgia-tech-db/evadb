import os
import pickle as pkl
import random

import numpy as np


def intersection_detector(image, scene, bboxes):
    # bboxes is a list of bounding boxes.
    # print(bboxes)
    intersections = []
    # TODO: need a keypoint dict
    keypoint_names = ["pt335", "pt342", "pt211", "pt208"]

    eva_loader_dir = os.path.dirname(os.path.abspath(__file__))
    keypoint_dict = pkl.load(
        open(os.path.join(eva_loader_dir, 'keypoint_dict'), 'rb'))
    if scene not in keypoint_dict:
        # If the scene is not defined in keypoint_dict, just make a random
        # keypoint list
        # TODO: When defining the keypoints, it should be (row, col) just as
        #  how we see it in an image
        scene_keypoints = np.array([[442.75, 100.98]])
        scene_threshold = 20.0
    else:
        scene_keypoints = np.array(keypoint_dict[scene]['keypoints'])
        scene_threshold = keypoint_dict[scene]['threshold']

    for bbox in bboxes:
        left = bbox[0]
        top = bbox[1]
        right = bbox[2]
        bottom = bbox[3]
        col = (left + right) / 2
        row = (top + bottom) / 2
        current_obj_location = np.array([row, col])

        detected_intersection = False
        for keypoint in scene_keypoints:
            distance = np.linalg.norm(keypoint - current_obj_location)
            # TODO: It would be nice if we can refer to the keypoints as [
            #  "pt335",
            #  "pt342", "pt211", "pt208"]
            if distance < scene_threshold:
                # TODO: Definitely need to fix this but for now, I will feed
                #  in
                #  random keypoint if it is close to any keypoint
                intersections.append(
                    keypoint_names[random.randint(0, len(keypoint_names) - 1)])
                detected_intersection = True
                break
        if detected_intersection is False:
            intersections.append(None)

    return intersections
