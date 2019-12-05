import cv2

def write_frames(path_from, path_to):

    cap = cv2.VideoCapture(path_from)

    while(cap.isOpened()):
        frameId = int(cap.get(1)) #current frame number
        framename = str(frameId)
        ret, frame = cap.read()
        pre = 15-len(framename)
        if (ret != True):
            break
        #storing frames in new folder 
        filename =path_to + '/frame_' + pre*'0' + framename + '.jpg'
        cv2.imwrite(filename, frame)
    cap.release()

    return