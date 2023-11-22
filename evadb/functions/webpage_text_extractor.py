from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
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

#testtest

def scrape_user_page(url):
    try:
        options = FirefoxOptions()
        options.add_argument("--headless")

        driver = webdriver.Firefox(options=options)

        driver.set_window_size(1920, 1080)
        # Open the GitHub user page
        driver.get(f"https://github.com/{url}")
        # driver.execute_script("document.body.style.zoom='120%'")

        # Capture the user profile section
        user_info_blocks = []
        try:
            user_info_blocks.append(driver.find_element(By.CLASS_NAME, "h-card"))
        except:
            pass
        info_ids = ["user-profile-frame", "user-private-profile-frame"]
        for info_id in info_ids:
            try:
                user_info_blocks.append(driver.find_element(By.ID, info_id))
            except:
                pass

        extracted_text = ""
        for info_block in user_info_blocks:
            screenshot = info_block.screenshot_as_png
            # with torch.cuda.device(gpu_id):
            result = reader.readtext(screenshot, detail=0)
            for i in result:
                extracted_text += i + " "

        return extracted_text

    except Exception as e:
        print(f"Error for {url}: {str(e)}")
        return str(e)
    finally:
        driver.quit()


# Define a function to extract text from a set of URLs
def extract_text_from_url(url):
    try:
        # Scrape user page using Selenium and EasyOCR
        extracted_text = scrape_user_page(url)
    except Exception as e:
        error_msg = f"Error extracting text from {url}: {str(e)}"
        print(error_msg)
        return error_msg

    return extracted_text


class WebPageTextExtractor(AbstractFunction):
    """
    Arguments:
        None

    Input Signatures:
        urls (list) : A list of URLs from which to extract text.

    Output Signatures:
        extracted_text (list) : A list of text extracted from the provided URLs.

    Example Usage:
        You can use this function to extract text from a list of URLs like this:

        urls = ["https://example.com/page1", "https://example.com/page2"]
    """

    @property
    def name(self) -> str:
        return "WebPageTextExtractor"

    @setup(cacheable=False, function_type="web-scraping")
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
        # Ensure URLs are provided
        if input_df.empty or input_df.iloc[0] is None:
            raise ValueError("URLs must be provided.")

        print(input_df)

        # Extract URLs from the DataFrame
        urls = input_df["github_username"]

        # Use ThreadPoolExecutor for concurrent processing
        num_workers = 1
        # Note: CUDA errors in EasyOCR with more than 1 worker
        ## profiling
        # 1 worker: 218.00s
        # 4 workers: 147.44s
        # 8 workers: 134.55s
        # 12 workers: 149.89s

        num_urls = len(urls)

        print(f"Extracting text from {num_urls} URLs using {num_workers} workers")

        start = time.time()
        extracted_text_lists = []
        # Use ThreadPoolExecutor for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit tasks to extract text from each URL
            extracted_text_lists = list(
                tqdm(executor.map(extract_text_from_url, urls), total=num_urls)
            )

        # Create a DataFrame from the extracted text
        extracted_text_df = pd.DataFrame({"extracted_text": extracted_text_lists})
        end = time.time()
        print("time taken: {:.2f}s".format(end - start))
        return extracted_text_df
