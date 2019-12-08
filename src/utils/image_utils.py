import numpy as np
import cv2


def convert_to_grayscale(frame):
    """
    Function  to convert a frame to grayscale

    :param frame: frame to be converted to grayscale
    :return frame after converting to grayscale
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def absolute_difference(curr_frame, prev_frame):
    """
    Function to find the absolute difference between two frames.
    Takes the sum of pixel wise difference.
    :param curr_frame: the current frame to be processed from the batch
    :param prev_frame: the previous frame that was not skipped
    """
    curr_frame_grayscale = convert_to_grayscale(curr_frame)
    prev_frame_grayscale = convert_to_grayscale(prev_frame)
    frame_diff = cv2.absdiff(curr_frame_grayscale, prev_frame_grayscale)
    return frame_diff.sum()


def mse_difference(curr_frame, prev_frame):
    """
    Function to find the mean squared error difference between two frames.
    :param curr_frame: the current frame to be processed from the batch
    :param prev_frame: the previous frame that was not skipped
    """
    curr_frame_gray = convert_to_grayscale(curr_frame)
    prev_frame_gray = convert_to_grayscale(prev_frame)
    total_pixels = curr_frame_gray.shape[0] * curr_frame_gray.shape[1]
    frame_diff = curr_frame_gray.astype('float') - prev_frame_gray
    mse_diff = np.sum(frame_diff**2) / float(total_pixels)
    return mse_diff


def mask_background(frame, dim=21, threshold1=10, threshold2=200, 
                    iterations=10, color=(0.0, 0.0, 0.0)):
    """
    Function that removes background from frame to help compare only
    foreground objects.
    :param frame: the current frame for which background needs to be masked
    :param dim: dimensions for Gaussian Blur
    :param threshold1, threshold2: the threshold values passed to the Canny
            function of cv2 to detect edges 
    :param iterations: defines the number of times dilation and erosion on
            need to be applied on images
    :param color: defines the color of the background pixels. 
                  Default color = Black
    :return masked_image: blackened out background for the passed frame
    """

    gray = convert_to_grayscale(frame)

    # Detect edges
    image_edges = cv2.Canny(gray, threshold1, threshold2)
    image_edges = cv2.dilate(image_edges, None)
    image_edges = cv2.erode(image_edges, None)

    contours_list = []
    contours, _ = cv2.findContours(
        image_edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    """
    If image has no contours, return image as it is
    """
    if len(contours) == 0:
        return frame

    for c in contours:
        contours_list.append((c, cv2.isContourConvex(c), cv2.contourArea(c),))

    """
    Get biggest contour
    """
    contours_list.sort(key=(lambda c: c[2]), reverse=True)
    max_contour = contours_list[0]

    """
    Create empty black mask. 
    Draw polygon corresponding to largest contour and fill with gray
    """
    background_mask = np.zeros(image_edges.shape)
    cv2.fillConvexPoly(background_mask, max_contour[0], (255))

    """
    Mask smoothening and blurring
    """
    background_mask = cv2.dilate(background_mask, None, iterations=iterations)
    background_mask = cv2.erode(background_mask, None, iterations=iterations)
    background_mask = cv2.GaussianBlur(background_mask, (dim, dim), 0)
    stacked_mask = np.dstack(3 * [background_mask])

    frame = frame / 255.0
    stacked_mask = stacked_mask / 255.0 
    
    masked_image = (stacked_mask * frame) + ((1 - stacked_mask) * color) 
    masked_image = (masked_image * 255).astype('uint8')

    return masked_image