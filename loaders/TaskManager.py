from loaders.color_detection import process_image
from loaders.intersection_detection import intersection_detector


class TaskManager():

    def __init__(self):
        self.images = None
        self.img_bboxes = None

    def call_color(self, image, img_bboxes):
        colors = []
        for bbox in img_bboxes:
            left = bbox[0]
            top = bbox[1]
            right = bbox[2]
            bottom = bbox[3]
            # image is already going to be an array

            img_to_pass = image[top:bottom, left:right, :]
            """
            if __debug__:
                print("inside task manager img shape is " + str(
                img_to_pass.shape))
                print("   original image shape is " + str(image.shape))
                print("   original image type is " + str(type(image)))
                print("(left, top, right, bottom coords are " + str((left, 
                top, right, bottom)))
            """
            color = process_image(img_to_pass).lower()
            if color != "":
                colors.append(color)
            else:
                colors.append(None)

        return colors

    def call_intersection(self, image, scene, img_bboxes):

        return intersection_detector(image, scene, img_bboxes)
