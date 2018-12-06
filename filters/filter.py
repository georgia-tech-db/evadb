import time
import os, sys
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import xml.etree.ElementTree as ET
import cv2
import sys
sys.path.append("/home/pballapuram3/Eva")
from faster_rcnn_pytorch.demo import accept_input_from_pp
def load_dataset(input_path):
	list_of_files = []
	num_frames_list = []
	for root, subdirs, files in os.walk(input_path):
		subdirs.sort()
		for dire in subdirs:
				listd = os.listdir(os.path.join(root,dire))
				num_frames_list.append(len(listd))
		for filename in sorted(files):
			file_path = os.path.join(root, filename)
			list_of_files.append(file_path)
	image_width = 960
	image_height = 540
	ratio = 12
	image_width = int(image_width/ratio)
	image_height = int(image_height/ratio)
	channels = 3
	X = np.ndarray(shape=(len(list_of_files), image_height, image_width, channels),dtype=np.float32)
	i = 0
	for file in list_of_files:
		img = cv2.imread(file)
		img=cv2.resize(img,(image_width,image_height))
		X[i] = np.asarray(img)
		X[i] = (X[i] - 128)/128
		i += 1
		if (i%10000 == 0):
			print ("Loaded %d images" %i)
	return X, num_frames_list

def get_vehtype_labels(filter, label_path, num_frames_list):
	y = []
	for root, subdirs, files in os.walk(label_path):
		i = 0
		for filename in sorted(files):
			file_path = os.path.join(root,filename)
			tree = ET.parse(file_path)
			tree_root = tree.getroot()
			j = 1
			#Frames without any vehicle detected don't have an entry in Annotations.xml, the code below first checks if the frame is in the annotation if not it sets
			#the label of the frame to 0, else checks against the filter to set it to 1 or 0. Finally we check if there are any frames not covered at the end of the
			#annotation file.
			for frame in tree_root.iter('frame'):
				if (int(frame.attrib['num'])!=j):
					for t in range(0,int(frame.attrib['num'])-j):
						y.append(0)
					j=int(frame.attrib['num'])
				flag = 0
				for attribute in frame.iter('attribute'):
					if (attribute.attrib['vehicle_type'] == filter):
						y.append(1)
						flag = 1
						break
				if (flag == 0):
					y.append(0)
				j+=1
			if (j!=num_frames_list[i]):
				for t in range(0,num_frames_list[i]-j+1):
					y.append(0)
				j=num_frames_list[i]
			i+=1
	return y

def PP(clf,X_train, X_test, y_train, y_test):
	train_start_time = time.time()
	clf.fit(X_train,y_train)
	print("train time: %.3f sec" % (time.time() - train_start_time))
	test_start_time = time.time()
	y_pred = clf.predict(X_test)
	print("test time: %.3f sec" % (time.time() - test_start_time))
	print ("Accuracy: %.3f"%clf.score(X_test,y_test))
	unique,counts = np.unique(y_pred,return_counts=True)
	print("Absolute reduction: ",counts[0],"/",len(y_test))
	print ("reduction rate: %.3f"%(counts[0]*1.0/len(y_test)))


#function to pass the frames that the trained classifer labels as 1 (in the test set) to the udf.
def pass_to_udf(test_pred,test_X):
	if len(test_X.shape)!=4:
		test_X=test_X.reshape(1,test_X.shape[0],test_X.shape[1],test_X.shape[2])
	pos_frames=np.where(test_pred==1)
	accept_input_from_pp(test_X[pos_frames])

def main():
	label_path = '../dataset/DETRAC-Train-Annotations-XML/'
	# label_path = '../dataset/small-annotation/'
	input_path = '../dataset/DETRAC-train-data/Insight-MVT_Annotation_Train/'
	# input_path = '../dataset/DETRAC-train-data/small-data/'
	vehtype_filters = ['car','van','bus']
	X, num_frames_list = load_dataset(input_path)
	nsamples, nx, ny, nc = X.shape
	X = X.reshape((nsamples,nx*ny*nc))
	print ("Loaded %d inputs"%len(X))
	for item in vehtype_filters:
		print ("--------------------Working on %s filter--------------------"%item)
		y = get_vehtype_labels(item, label_path, num_frames_list)
		y = np.array(y)
		# print "number of ",item, unique[1],counts[1]
		# print ("Loaded %d labels"%len(y))
		X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.33, random_state=42)
		unique,counts = np.unique(y_test,return_counts=True)
		print ("No.of test frames without cars :",counts[0],"/",len(y_test))
		########## Linear SVC ############
		clf = LinearSVC(random_state=0)
		print ("--- LinearSVC ---")
		PP(clf,X_train, X_test, y_train, y_test)
		######### Random Forest ###########
		clf = RandomForestClassifier(max_depth=2, random_state=0)
		print ("--- RandomForest ---")
		PP(clf,X_train, X_test, y_train, y_test)
	# X =

if __name__ == '__main__':
	start_time = time.time()
	#main()
	img=[]
	for i in range(1781,1791):
		img.append(np.asarray(cv2.imread("img0"+str(i)+".jpg")))
	img=np.asarray(img)
	print(img.shape)
	pass_to_udf(np.asarray([1,1,1,1,1,1,1,1,1,1]),img)
	print("--- Total Execution Time : %.3f seconds ---" % (time.time() - start_time))
