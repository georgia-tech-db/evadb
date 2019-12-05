'''
This function takes in index_list, data_path , save_path as the arguments. It writes a video consisting 
of the frame in data_path into save_path and writes a text file with the indexed of the representative 
frame into the same directory 
'''

import cv2
import os
import imageio
from glob import glob

def write_data(index_list,data_path='',save_path='',Detrac = False):
    
    p = save_path.split('/')
    
    index_path = ''
    for i in p[:-1]:
        index_path+=i + '/'
    
    with open(index_path + 'representative_frame.txt', 'w') as f:
        for item in index_list:
            f.write("%s\n" % item)
    
        
        
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
        frames = glob( data_path + '/*jpg') 
        frames = sorted(frames)
        img_for_shape = imageio.imread( frames[0] )
        width = img_for_shape.shape[1]
        height = img_for_shape.shape[0]
        video = cv2.VideoWriter(save_path,fourcc,30, (width,height))
        for f in frames:
            #print(f)
            img = imageio.imread( f )
            video.write(img)
    
        video.release()
        cv2.destroyAllWindows()

        
        