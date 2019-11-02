from src.editing_opr.image_opr import ImageOperations


class Operator:
    def __init__(self):
        pass

    @staticmethod
    def apply(opr, images, args=None):
        if opr == 'grayscale':
            images = ImageOperations.grayscale(images)
            return images
        elif opr == 'blur':
            images = ImageOperations.blur(images, args['kernel_size'])
            return images

    @staticmethod
    def transform(opr_list, images, args=None):
        for opr in opr_list:
            images = Operator.apply(opr, images, args)
        return images
