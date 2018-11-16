import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np

from PIL import Image
import cv2



#im = np.array(Image.open('./MVI_20011/img00001.jpg'), dtype=np.uint8)

x,y = 592,378
h,w = 160,162


def intersection_detector(image, scene, bboxes):
	#bboxes is a list of bounding boxes.
	print(bboxes)




	''' uncomment this section to actually do the detection '''
	# keypoint_dict= pkl.load('keypoint_dict')
	# scene_keypoints  = np.array(keypoint_dict['scene']['keypoints'])
	# scene_threshold  = keypoint_dict['scene']['threshold']

	# current_obj_location = np.array([x,y])

	# distance = np.linalg.norm(scene_keypoints-current_obj_location)
	# if distance<scene_threshold:
	# 	i = 1
	# else:
	# 	i = 0

	## remove this line later to not hardcode the intersection value
	i =1

	return i