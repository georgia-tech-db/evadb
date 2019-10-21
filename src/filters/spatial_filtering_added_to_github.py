from utils import CFEVideoConf
import math
from skimage.exposure import rescale_intensity
import numpy as np
import cv2

def verify_alpha_channel(frame):
    try:
        frame.shape[3] # 4th position
    except IndexError:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    return frame

def convolution(frame, kernel):
	frame = verify_alpha_channel(frame)
    frame_h, frame_w, frame_c = frame.shape
	kernel_h, kernel_w, kernel_c=kernel.shape
	# padding the image to deal with border pixels
	pad = (kernel_w - 1) // 2
	frame = cv2.copyMakeBorder(frame, pad, pad, pad, pad,
		cv2.BORDER_REPLICATE)
	output = np.zeros((frame_h, frame_w), dtype="float32")
	for y in np.arange(pad, frame_h + pad):
		for x in np.arange(pad, frame_w + pad):
			portion=frame[y - pad:y + pad + 1, x - pad:x + pad + 1]
			# summation of the element-wise multiplicate between the portion and
			# the kernel
			k = (portion * kernel).sum()
			output[y - pad, x - pad] = k
	output = rescale_intensity(output, in_range=(0, 255))
	output = (output * 255).astype("uint8")
	frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    return output,frame
