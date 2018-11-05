from filters.color_detection import process_image

class TaskManager():

    def __init__(self,images,img_bbox,img_class):
        self.images=images
        self.img_bbox=img_bbox
        self.img_class=img_class

    def call_color(self):
        color = []
        for img in self.images:
            for bbox in self.img_bbox:
                img_to_pass = img[bbox]
                color.append(process_image(img_to_pass))
        return color

    def call_speed(self):
        pass

    def call_bi(self):
        pass