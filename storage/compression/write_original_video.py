'''
This function takes in index_list, data_path , save_path as the arguments. It writes a video consisting 
of the frame in data_path into save_path and writes a text file with the indexed of the representative 
frame into the same directory 

inputs :

    - frames = list of frames i.e. numpy arrays
    - scale = scale to resize, int
    - data_path = path to original data, string
    - save_original_path = path to save scaled video, string
    - Detrac = For development purposes only, True
    
outputs : None

'''

import cv2
import os
import imageio
from glob import glob
from tqdm import tqdm

def write_original_video(frames, scale=1 , data_path='', save_original_path='' ,Detrac = False):

    if Detrac:
        c = 0
        width = 960
        height = 540
        fourcc = cv2.VideoWriter_fourcc(*'MP42')
        for i in os.listdir('DETRAC-Images/'):
            video = cv2.VideoWriter('./DETRAC_video.avi',fourcc,30, (width,height))
            for j in range(1, len(os.listdir('DETRAC-Images/' + i + '/'))+1):
                j = str(j)
                jj= 5-len(j)
                k = "img" + jj*"0" +j +".jpg"
                img = imageio.imread('DETRAC-Images/' + i + '/' + k + '/')
                video.write(img)
                
            video.release()
            cv2.destroyAllWindows()
            break
            
        video.release()
        cv2.destroyAllWindows()

    else:
        
        c = 0
        
        fourcc = cv2.VideoWriter_fourcc(*'MP42')
        
        if type(scale) == tuple:
            width = scale[1]
            height = scale[0]
        
        else:
            cap = cv2.VideoCapture(data_path)
            ret, img_for_shape = cap.read()
            cap.release()
            width = float(scale) * int(img_for_shape.shape[1])
            height = float(scale) * int(img_for_shape.shape[0])
        
        width = int(width)
        height = int(height)
        video = cv2.VideoWriter(save_original_path,fourcc,30, (width,height))
        print()
        for img in tqdm(list(frames)):
            img = cv2.resize( img , (width, height))
            video.write(img)
    
        video.release()
        cv2.destroyAllWindows()

        
        