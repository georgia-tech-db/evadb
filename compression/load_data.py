from glob import glob
from tqdm import tqdm
import imageio
import numpy as np
import cv2
import torch 
import torch.utils as utils
import os
import torch.utils.data as utils


"""
Data Loader function handles both scenarios where UE-DETRAC dataset is 
true or not. Data must have a clearly sequential naming convention to 
ensure that frames are stored in the same order in the folder as they are 
in the video. e.g frame_1 --> frame_00001 when there are less than 10000 
frames. Failure to do so will result in frames misordering such as 
frame_1,frame_10 appearing next to one another

Inputs: path to the datasets files, flag to use UE-DETRAC data

Output: loaded data resized to 100x100 tensor ready to input into the dataset
"""
def load_data(path, detrac = False, train = False):

    
    data = []
    #detrac had an unconventional naming sequence that needs to be accounted seperately so as to not mix up the frame order
    #note that this was simply for testing functionality on the first video in detrac
    
    print( '\n Loading Data .. \n')
    
    if detrac:
        c = 0
        for i in os.listdir('DETRAC-Images/'):
            n_data = []
            c+=1
            for j in tqdm(range(1, len(os.listdir('DETRAC-Images/' + i + '/'))+1)):
                j = str(j)
                jj= 5-len(j)
                k = "img" + jj*"0" +j +".jpg"
                img = imageio.imread('DETRAC-Images/' + i + '/' + k + '/')
                #print("image", img)
                n_data.append(cv2.resize(img, (100, 100), interpolation = cv2.INTER_AREA))
            n_data = np.array(n_data)
            data = n_data.copy()
            break
        
    else:
        frames = glob(path + '/*.jpg')
        
        for f in tqdm(frames):
            img = imageio.imread(f)
            data.append(cv2.resize(img, (100, 100), interpolation = cv2.INTER_AREA))
                         
    data_load = np.array(data).transpose(0,3,1,2)
    
    data_load= (data_load - 255) / 255

    batch_size = 8

    print( ' \n Creating dataloader ..')
    
    tensor_x = torch.stack([torch.Tensor(i) for i in data_load])

    train_dataset = utils.TensorDataset(tensor_x,tensor_x)
    train_loader = utils.DataLoader(train_dataset, batch_size=batch_size, shuffle = train)

    return train_loader