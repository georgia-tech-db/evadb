import cv2
import os
import argparse

'''
This function is used to read in the data 
and return a list of frames as 3 dimensinal
numpy images.

Input : relative path to inpyt video

Output : list of numpy array 
'''

def preprocessing( path_from ):
    
    print('\n Preprocessing ..\n')
    cap = cv2.VideoCapture(path_from)

    frame_list=[]
    while(cap.isOpened()):
        frameId = int(cap.get(1)) #current frame number
        framename = str(frameId)
        ret, frame = cap.read()
        if (ret != True):
            break
        frame_list.append( frame )
        
    return frame_list
        