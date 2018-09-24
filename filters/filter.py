import time
import os, sys
import numpy as np
from sklearn import tree
from sklearn.svm import LinearSVC
#import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import xml.etree.ElementTree as ET
from scipy import ndimage
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

def load_dataset(input_path):
	list_of_files = []
	for root, subdirs, files in os.walk(input_path):
		subdirs.sort()
		for filename in sorted(files):
			file_path = os.path.join(root, filename)
			list_of_files.append(file_path)
			# print('\t- file %s (full path: %s)' % (filename, file_path))
	print len(list_of_files)
	image_width = 960
	image_height = 540
	ratio = 12
	image_width = int(image_width/ratio)
	image_height = int(image_height/ratio)
	channels = 3
	X = np.ndarray(shape=(len(list_of_files), image_height, image_width, channels),dtype=np.float32)
	i = 0
	for file in list_of_files:
		img = load_img(file, target_size=(image_height, image_width))
		X[i] = img_to_array(img)
		X[i] = (X[i] - 128)/128
		i += 1
		if (i%1000 == 0):
			print ("Loaded %d images" %i)
	return X			
def get_labels(filter, label_path):
	
	return 1


def main():
	label_path = '../dataset/DETRAC-Train-Annotations-XML/'
	input_path = '../dataset/DETRAC-train-data/Insight-MVT_Annotation_Train/'
	filters = ['car', 'van', 'bus']
	X = load_dataset(input_path)
	for item in filters:
		y = get_labels(item, label_path)
	# 	X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.2, random_state=33)
	# 	clf = LinearSVC(random_state=0)
	# 	clf.fit(X_train,y_train)
	# xml_tree = ET.parse()
	# X = 

if __name__ == '__main__':
	start_time = time.time()
	main()
	print("--- %s seconds ---" % (time.time() - start_time))
