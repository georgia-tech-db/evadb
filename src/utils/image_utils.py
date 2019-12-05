import numpy as np
import cv2


def convert_to_grayscale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def absolute_difference(curr_frame, prev_frame):
    curr_frame_grayscale = convert_to_grayscale(curr_frame)
    prev_frame_grayscale = convert_to_grayscale(prev_frame)
    frame_diff = cv2.absdiff(curr_frame_grayscale, prev_frame_grayscale)
    return frame_diff.sum()


def mse_difference(curr_frame, prev_frame):
    curr_frame_gray = convert_to_grayscale(curr_frame)
    prev_frame_gray = convert_to_grayscale(prev_frame)
    total_pixels = curr_frame_gray.shape[0] * curr_frame_gray.shape[1]
    frame_diff = curr_frame_gray.astype('float') - prev_frame_gray
    mse_diff = np.sum(frame_diff**2) / float(total_pixels)
    return mse_diff


# Function to blacken out background of frame
def mask_background(frame, dim=21, threshold1=10, threshold2=200, 
                    iterations=10, color=(0.0, 0.0, 0.0)):
    gray = convert_to_grayscale(frame)

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
    contours_list.sort(key=(lambda c: c[2]), reverse=True)
    max_contour = contours_list[0]

    # Create empty black mask. 
    # Draw polygon corresponding to largest contour and fill with gray
    background_mask = np.zeros(image_edges.shape)
    cv2.fillConvexPoly(background_mask, max_contour[0], (255))

    # Mask smoothening and blurring
    background_mask = cv2.dilate(background_mask, None, iterations=iterations)
    background_mask = cv2.erode(background_mask, None, iterations=iterations)
    background_mask = cv2.GaussianBlur(background_mask, (dim, dim), 0)
    stacked_mask = np.dstack(3 * [background_mask])

    frame = frame / 255.0
    stacked_mask = stacked_mask / 255.0 
    
    masked_image = (stacked_mask * frame) + ((1 - stacked_mask) * color) 
    masked_image = (masked_image * 255).astype('uint8')

    return masked_image