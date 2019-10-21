import os, sys
import time
import numpy as np
import cv2

def temporal_filter(video_name, time_start, time_end):
	time_start = int(time_start[0]) * 60 + int(time_start[2:4])
	time_end = int(time_end[0]) * 60 + int(time_end[2:4])

	cap = cv2.VideoCapture(video_name)

	totalframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	fps = int(cap.get(cv2.CAP_PROP_FPS))
	totaltime = float(totalframes) / float(fps)

	if time_start < 0 or time_start > time_end or time_start > totaltime:
		print("invalid time")
		cap.release()

	elif time_end < 0  or time_end > totaltime:
		print("invalid time")
		cap.release()

	if (cap.isOpened() == False):
		print("error opening the file")

	if (cap.isOpened() == True):
		cap.set(1, time_start * fps)
	start = time.time()
	while (cap.isOpened()):

		ret, frames = cap.read()

		if cap.get(1) > (time_end * fps):
				break
				
		if ret == True:
			cv2.imshow("Frame", frames)
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break
			
		else:
			break

	end = time.time()
	print(end - start)
	cap.release()
	cv2.destroyAllWindows()



if __name__ == "__main__":
	vid_name = str(sys.argv[1])
	time_s = input('What time do you want to start (in minute:second format)?')
	time_f = input('What time do you want to end (in minute:second format)?')
	temporal_filter(vid_name, time_s, time_f)