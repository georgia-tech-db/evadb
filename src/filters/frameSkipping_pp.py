from abstract_pp import AbstractPP
from src.utils import image_utils


class frameSkippingPP(AbstractPP):

    def __init__(threshold, compare_foreground, distance_metric):
        self.threshold = threshold
        self.compare_foreground = compare_foreground
        self.distance_metric = distance_metric

    def predict(self, batch) -> List[bool]:
        frames = batch.frames().tolist()
        prev_frame = None
        skipFrames = []
        for frame in frames:
            if prev_frame is not None:
                """
                If compare_foreground set to true, calculate distance
                metric on only the foreground pixels
                else on the entire image.
                """
                if self.compare_foreground is True:
                    frame_diff = self.compare_foreground_mask(
                        frame, prev_frame, self.distance_metric)
                else: 
                    frame_diff = self.frame_difference(
                        frame, prev_frame, self.distance_metric)
                if frame_diff < self.threshold:
                    skipFrames.append(True)
                else:
                    skipFrames.append(False)
                    prev_frame = frame
            else:
                skipFrames.append(False)
                prev_frame = frame
        return skipFrames

    # Function to calculate frame difference based on distance metric

    def frame_difference(self, curr_frame, prev_frame, distance_metric):
        diff = getattr(image_utils, distance_metric)
        frame_diff = diff(curr_frame, prev_frame)
        return frame_diff

    def compare_foreground_mask(self, curr_frame, prev_frame, distance_metric):
        # curr_foreground = mask_background(curr_frame)
        # prev_foreground = mask_background(prev_frame)
        # return frame_difference(curr_foreground, prev_foreground, distance_metric)
        pass