class FrameFilter:
    """

        class for implementing spatial frame filtering feature in depth estimation.
       It takes one frame at a time, calculates a pixel mask to ignore the pixels which are too far in the image.
       We want to restrict the pixel masking only to the upper portion of image where the sky is present.
       After the frame processing is done by this class, the all the sky region in the frame will black out.

       Arguments:

    """

    def __init__(self):
        """
        Initialization method for frame filtering object.
        Sets the index value to 0. We need to apply mask to every non fifth frame.

        Arguments:

        """

        self.current_frame_index = 0

    def apply_filter(self, img, d_mask):
        """
        Receives frame and mask as input. Applies mask to all incoming frames except every 5th frame. At every 5th frame, we recreate a new image mask.
        Arguments:
                img (np.ndarray): Single frame of image
                d_mask (np.ndarray): Image mask for frame filtering
        Returns:
                img : image after applying the filtering mask

        """

        if self.current_frame_index % 5 != 0:
            img = img*d_mask[:, :, None]

        self.current_frame_index += 1

        return img


