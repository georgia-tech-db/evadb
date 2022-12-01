import pytesseract
# from PIL import Image
from detoxify import Detoxify
import pandas as pd


class HarmfulMemeDetector(PytorchAbstractClassifierUDF):
    """
    Arguments:
        threshold (float): Threshold for classifier confidence score

    """

    @property
    def name(self) -> str:
        return "harmfulMeme"

    def setup(self, threshold=0.2):
        self.threshold = threshold
        # self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
        #     pretrained=True, progress=False
        # )
        # self.model.eval()

    # @property
    # def input_format(self) -> FrameInfo:
    #     return FrameInfo(-1, -1, 3, ColorSpace.RGB)

    def forward(self, this_image):

        text = pytesseract.image_to_string(this_image)
        prediction_result = Detoxify('original').predict(text)
        outcome = pd.DataFrame()
        if prediction_result["toxicity"] >= self.threshold:
            outcome = outcome.append("toxic")
        else:
            outcome = outcome.append("not toxic")
        for key in prediction_result.keys():
            if key == "toxicity":
                continue
            if prediction_result[key] >= self.threshold:
                outcome = outcome.append(key)
        return outcome
