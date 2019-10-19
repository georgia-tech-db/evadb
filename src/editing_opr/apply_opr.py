from src.editing_opr.grayscale import Grayscale


class ApplyOpr:
    def __init__(self):
        pass

    @staticmethod
    def apply(loader, video_id):
        images = loader.load_cached_images(video_id)
        edited_images = Grayscale.convert(images)
        loader.save_images(edited_images, video_id)