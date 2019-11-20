import cv2
import numpy as np

"""

Utility functions to calculate inter-frame difference

"""

class DistanceMetrics:
	def convert_to_grayscale(self, frame):
		return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		#return frame

	def absolute_difference(self, curr_frame, prev_frame):
		curr_frame_grayscale = self.convert_to_grayscale(curr_frame)
		prev_frame_grayscale = self.convert_to_grayscale(prev_frame)
		frame_diff = cv2.absdiff(curr_frame_grayscale, prev_frame_grayscale)
		return frame_diff.sum()

	def mse_difference(self, curr_frame, prev_frame):
		curr_frame_grayscale = self.convert_to_grayscale(curr_frame)
		prev_frame_grayscale = self.convert_to_grayscale(prev_frame)
		total_pixels = curr_frame_grayscale.shape[0]*curr_frame_grayscale.shape[1]
		frame_diff = curr_frame_grayscale.astype('float') - prev_frame_grayscale
		mse_diff = np.sum(frame_diff**2)/float(total_pixels)
		return mse_diff

# Function to blacken out background of frame
def mask_background(frame):
	# Initialize paramaters
    dim = 21

    # Thresholds for detecting edges
    threshold1 = 10
    threshold2 = 200

    iterations = 10

    # Mask (Black) in BGR format
    color_black = (0.0,0.0,0.0) 

    gray = DistanceMetrics().convert_to_grayscale(frame)

    # Detect edges
    image_edges = cv2.Canny(gray, threshold1, threshold2)
    image_edges = cv2.dilate(image_edges, None)
    image_edges = cv2.erode(image_edges, None)

    contours_list = []
    contours, _ = cv2.findContours(
    	image_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # If image has no contours, return image as it is
    if len(contours) == 0:
    	return frame

    for c in contours:
    	contours_list.append((c, cv2.isContourConvex(c), cv2.contourArea(c),))

    # Get biggest contour
    contours_list.sort(key = (lambda c : c[2]), reverse = True)
    max_contour = contours_list[0]

    # Create empty black mask. Draw polygon corresponding to largest contour and fill with gray
    background_mask = np.zeros(image_edges.shape)
    cv2.fillConvexPoly(background_mask, max_contour[0], (255))

    # Mask smoothening and blurring
    background_mask = cv2.dilate(background_mask, None, iterations=iterations)
    background_mask = cv2.erode(background_mask, None, iterations=iterations)
    background_mask = cv2.GaussianBlur(background_mask, (dim, dim), 0)
    stacked_mask = np.dstack(3 * [background_mask])

    frame = frame / 255.0
    stacked_mask  = stacked_mask / 255.0 
     
    masked_image = (stacked_mask * frame) + ( (1 - stacked_mask) * color_black) 
    masked_image = (masked_image * 255).astype('uint8')

    return masked_image

# Function to calculate frame difference based on distance metric
def frame_difference(curr_frame, prev_frame, distance_metric):
	distance_metrics = DistanceMetrics()
	diff = getattr(distance_metrics, distance_metric)
	frame_diff = diff(curr_frame, prev_frame)
	return frame_diff

def compare_foreground_mask(curr_frame, prev_frame, distance_metric):
	curr_foreground = mask_background(curr_frame)
	prev_foreground = mask_background(prev_frame)
	return frame_difference(curr_foreground, prev_foreground, distance_metric)