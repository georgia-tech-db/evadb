import concurrent.futures
import pandas as pd
import time
from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe

import easyocr
from tqdm import tqdm


reader = easyocr.Reader(["en"], gpu=True)


def extract_text(image_path):
    try:
        extracted_text = ""
        result = reader.readtext(image_path, detail=0)
            for element in result:
                extracted_text += element + " "
        return extracted_text

    except Exception as e:
        print(f"Error for {image_path}: {str(e)}")
        return str(e)

def get_text_from_image(path):
    try:
        # Extract text using EasyOCR
        extracted_text = extract_text(path)
    except Exception as e:
        error_msg = f"Error extracting text from {path}: {str(e)}"
        print(error_msg)
        return error_msg
    return extracted_text


class WebPageTextExtractor(AbstractFunction):
    """
    Arguments:
        None

    Input Signatures:
        image_path (str) : The path to image from which to extract text.

    Output Signatures:
        extracted_text (list) : A list of text extracted from the provided image.

    Example Usage:
        You can use this function to extract text from an image
    """

    @property
    def name(self) -> str:
        return "ImageTextRecognizer"

    @setup(cacheable=False, function_type="text-recognition")
    def setup(self) -> None:
        pass

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["image_path"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["extracted_text"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, input_df):
        if input_df.empty or input_df.iloc[0] is None:
            raise ValueError("A path to image must be provided.")

        print(input_df)

        paths = input_df["path"]

        num_workers = 1

        start = time.time()
        extracted_text_lists = []
        # Use ThreadPoolExecutor for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit tasks to extract text from each URL
            extracted_text_lists = list(
                tqdm(executor.map(get_text_from_image, paths), total=len(paths))
            )

        # Create a DataFrame from the extracted text
        extracted_text_df = pd.DataFrame({"extracted_text": extracted_text_lists})
        end = time.time()
        print("time taken: {:.2f}s".format(end - start))
        return extracted_text_df
