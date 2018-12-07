import numpy as np
import pickle as pkl


def intersection_detector(image, scene, bboxes):
  #bboxes is a list of bounding boxes.
  print(bboxes)
  intersections = []
  #TODO: need a keypoint dict

  keypoint_dict= pkl.load('keypoint_dict')
  scene_keypoints  = np.array(keypoint_dict['scene']['keypoints'])
  scene_threshold  = keypoint_dict['scene']['threshold']

  for bbox in bboxes:
    left = bbox[0]
    top = bbox[1]
    right = bbox[2]
    bottom = bbox[3]
    x = (left + right) / 2
    y = (top + bottom) / 2
    current_obj_location = np.array([x,y])

    detected_intersection = False
    for keypoint in scene_keypoints:
      distance = np.linalg.norm(keypoint-current_obj_location)
    #TODO: It would be nice if we can refer to the keypoints as ["pt335", "pt342", "pt211", "pt208"]
      if distance < scene_threshold:
        intersections.append(keypoint)
        detected_intersection = True
        break
    if detected_intersection == False:
      intersections.append(None)

  return intersections

