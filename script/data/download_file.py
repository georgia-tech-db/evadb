import os
import requests
import sys

from tqdm import tqdm

# map file names to their corresponding google drive ids
file_id_map = {

    # datasets
    "bdd_test" : "1FQVygs5yOUz0Zv2uhk1VcrJjYDzVJ1T8",

    # models
    "vehicle_make_predictor" : "1pM3FFlSMWhZ4LYpdL2tNRvofUKzifzZe"
    
}

def download_file_from_google_drive(file_name, destination):
    """
    Downloads a zip file from google drive. Assumes the file has open access. 
    Args:
        file_name: name of the file to download
        destination: path to save the file to
    """

    URL = "https://drive.google.com/uc?export=download"

    # fetch the id of the file to download
    id = file_id_map[file_name]

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    """
    Returns the confirm token from the response.
    Args:
        response: response object from the request
    """

    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    """
    Writes the content of the response to the destination. 
    Args:
        response: response object from the request
        destination: path to save the file to
    """
    
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in tqdm(response.iter_content(CHUNK_SIZE)):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

if __name__ == "__main__":
    file_name = sys.argv[1]
    destination = os.path.join(os.getcwd(), file_name + ".zip")
    download_file_from_google_drive(file_name, destination)
