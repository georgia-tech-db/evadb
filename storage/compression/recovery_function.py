import numpy as np
import cv2
from tqdm import tqdm

"""
Recovery Function takes a query of frames from a compressed video and returns the original frames of the video,
function needs the compressed videos meta data and returns two lists, one list contains lists of rame sequences in the order
of the indexes passed to the function, the latter contains a flattten version of this list for visualization purposes

Inputs: 
    - frame_array : List of compressed video frame indexes being queried
    - metadata : the metadata of the compressed video 

Output: 
    - final_restruct_output_frames : List of Lists of frames  
    - final_restruct_output_frames_flat : List of frames 
    
"""

#dummy class meant to simulate video info class
class meta:
    def __init__(self,original_path,compressed_index, compressed = True):
        self.original_path = original_path
        self.compressed_index = compressed_index
        self.compressed = compressed 
        

def recovery_function(frame_array, metadata):
    print( '\n Recovering frames .. ')
    if not metadata.compressed:
        print("This is not a compressed video... No need to recover frames")
        return [],[]
    
    path = metadata.original_path
    
    frame_array = np.array(frame_array)

    sorted_frame_array = sorted(frame_array)
    arg_array = frame_array.argsort()
    arg_array = arg_array.argsort()
    
    
    frames = []
    flat_frames = []
    clip_lengths = []

    for cf in sorted_frame_array:
        subframes = list(range(metadata.compressed_index[cf] , metadata.compressed_index[cf+1]))
        frames.append(subframes)
        flat_frames.extend(subframes)
        clip_lengths.append(len(subframes))
    
    cap = cv2.VideoCapture(path)   

    output_frames = []

    c = 0

    while(cap.isOpened()):
        frameId = int(cap.get(1)) #current frame number
        
        ret, frame = cap.read()
        if (ret != True):
            break

        if frameId == flat_frames[c]:
            output_frames.append(frame)
            if c < (len(flat_frames) -1):
                c+=1
            else:
                break

    cap.release()
        

    restruct_output_frames = []

    c = 0

    for l in clip_lengths:
        subframes = output_frames[c:c+l]
        c += l
        restruct_output_frames.append(subframes)

    
    final_restruct_output_frames = [] 
    final_restruct_output_frames_flat = []
    
    for arg in arg_array:
        final_restruct_output_frames.append(restruct_output_frames[arg])
        final_restruct_output_frames_flat.extend(restruct_output_frames[arg])
        
    return final_restruct_output_frames, final_restruct_output_frames_flat
        
    
        
        

    


        

