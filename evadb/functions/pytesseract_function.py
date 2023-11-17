import pandas as pd
import numpy as np
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe
from evadb.catalog.catalog_type import NdArrayType
import ast

from evadb.utils.generic_utils import try_to_import_pytesseract


class PyTesseractOCRFunction(AbstractFunction):
    @property
    def name(self) -> str:
        return "PyTesseractOCRFunction"
    
    @setup(cacheable=False, function_type="FeatureExtraction", batchable=False)
    def setup(self,\
            convert_to_grayscale: str, \
            remove_noise: str, \
            tesseract_path:str = None) -> None: # type: ignore
        
        try_to_import_pytesseract()
        
        #set the tesseract engine
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        self.grayscale_flag = convert_to_grayscale
        self.remove_noise = remove_noise
        

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT64],
                column_shapes=[(None, 3)],
            ),

        ],
        output_signatures=[
            PandasDataframe(
                columns=["text"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, frames: pd.DataFrame) -> pd.DataFrame:

        img_data = np.asarray(frames['data'][0])

        if ast.literal_eval(self.grayscale_flag):
            img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2GRAY)
        
        if ast.literal_eval(self.remove_noise):
            img_data = cv2.medianBlur(img_data,5)

        
        #apply the OCR
        text = pytesseract.image_to_string(img_data)

        new_df = {"text": [text]}

        return pd.DataFrame(new_df)
        

    

    

