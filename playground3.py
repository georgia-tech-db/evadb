import evadb
import time
import cProfile
import pandas as pd
from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe

class WebPageTextExtractor(AbstractFunction):
    @property
    def name(self) -> str:
        return "WebPageTextExtractor"

    @setup(cacheable=True, function_type="web-scraping")
    def setup(self) -> None:
        # Any setup or initialization can be done here if needed
        pass

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["urls"],
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
        # Create a DataFrame from the extracted text
        extracted_text_lists = []
        for _, row in input_df.iterrows():
            urls = row.iloc[0]
            time.sleep(1)
            extracted_text_lists.append(f"E({urls})")

        extracted_text_df = pd.DataFrame({"extracted_text": extracted_text_lists})
        return extracted_text_df

class LLMExtractor(AbstractFunction):
    @property
    def name(self) -> str:
        return "LLMExtractor"

    @setup(cacheable=True, function_type="llm-extractor")
    def setup(self) -> None:
        # Any setup or initialization can be done here if needed
        pass

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["prompt", "content"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["response"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, input_df):
        # Create a DataFrame from the extracted text
        response_lists = []
        for _, row in input_df.iterrows():
            prompt = row.iloc[0]
            content = row.iloc[1]
            time.sleep(1)
            response_lists.append(f"L({prompt}, {content})")

        extracted_text_df = pd.DataFrame({"response": response_lists})
        return extracted_text_df

class LLMBatch(AbstractFunction):
    @property
    def name(self) -> str:
        return "LLMBatch"

    @setup(cacheable=True, function_type="llm-batch")
    def setup(self) -> None:
        # Any setup or initialization can be done here if needed
        pass

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["prompt", "content"],
                column_types=[NdArrayType.STR, NdArrayType.STR],
                column_shapes=[(None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["response"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, input_df):
        # Create a DataFrame from the extracted text
        response_lists = []
        for _, row in input_df.iterrows():
            prompt = row.iloc[0]
            content = row.iloc[1]
            response_lists.append(f"B({prompt}, {content})")

        time.sleep(1)
        extracted_text_df = pd.DataFrame({"response": response_lists})
        return extracted_text_df



if __name__ == "__main__":
    cursor = evadb.connect().cursor()
    
    params = {
        "owner": "georgia-tech-db",
        "repo": "evadb",
        "github_token": "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",
    }
    
    cursor.query("DROP DATABASE IF EXISTS github_data;").df()
    
    query = f"""CREATE DATABASE IF NOT EXISTS github_data
                WITH ENGINE = "github",
                PARAMETERS = {params};"""
    cursor.query(query).df()
    
    
    query = f"CREATE OR REPLACE FUNCTION WebPageTextExtractor IMPL 'playground3.py';"
    cursor.query(query).df()
    
    query = f"CREATE OR REPLACE FUNCTION LLMExtractor IMPL 'playground3.py';"
    cursor.query(query).df()

    query = f"CREATE OR REPLACE FUNCTION LLMBatch IMPL 'playground3.py';"
    cursor.query(query).df()

    start = time.perf_counter()
    query = """
        SELECT name, followers, LLMBatch("S", lang) FROM github_data.stargazers 
        JOIN LATERAL WebPageTextExtractor(name) AS web(text)
        JOIN LATERAL LLMExtractor("P", text) AS golden(lang)
        WHERE followers > 100
        LIMIT 10;
    """
    baseline_query = "SELECT name2 FROM github_data.stargazers WHERE followers > 100 LIMIT 10;"
    res = cursor.query(baseline_query).df()
    end = time.perf_counter()
    print(res)
    print(end-start)
