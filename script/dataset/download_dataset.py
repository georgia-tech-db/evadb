import os
import requests
import sys

from tqdm import tqdm

# map dataset names to their google drive ids
dataset_id_map = {
    "bdd_test" : "1FQVygs5yOUz0Zv2uhk1VcrJjYDzVJ1T8"
}

def download_file_from_google_drive(dataset_name, destination):
    URL = "https://drive.google.com/uc?export=download"

    # fetch the id of the file to download
    id = dataset_id_map[dataset_name]

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in tqdm(response.iter_content(CHUNK_SIZE)):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

if __name__ == "__main__":
    dataset_name = sys.argv[1]
    destination = os.path.join(os.getcwd(), dataset_name + ".zip")
    download_file_from_google_drive(dataset_name, destination)
