

# Eva Storage Module README

### The storage module provides end to end help reducing the input datasize for fast video analytics.


#### Functionality within this module:
1. Using a pre-trained model on the UE-DETRAC Dataset to get compressed clustered representations.
2. Training the model on your own data to get a latent representation optimized for your own input video.


#### Primary Outputs:
- `_.txt` file with the indexes of the representative frames from your input dataset. (Can use UE-DETRAC)
- `_.avi` compressed video in mp4 version. Can be used to extract representative frames within the video dataset.


## Usage:

##### Use the `download_files.sh` to download the pretrained model file and testing video


1. If using UE-DETRAC dataset user can skip directly to the main function.
2. Using your own individual video, the video likely needs to be preprocesed and files need to be labelled in sequential order for input to train function.

### preprocessing.py
Use `preprocessing.py` to format your video into sequentially labelled frames for training.

Preprocessing functionality can be browsed with the help command:

`>>> python preprocessing.py -h`


There are two required inputs:<br/>
`path_from`: Add path to actual video which needs to be transformed into sequential frames<br/>
`path_to`: Add path to folder where output frames will be same


### Main.py

Main functionality can be browsed with the help command:

`>>> python Main.py -h`


Main function has the following inputs:<br/>
`-train` : Boolean flag to check whether to train the auto-encoder  <br/>
`-DETRAC`: Boolean flag to use DETRAC dataset<br/>
`-verbose`: Boolean flag to print losses in each iteration of training <br/>

**Functionality needed only for custome video input**<br/>
`-path` : String original path to video frames *(please see `preprocess_data.py`)*<br/>
`-save_path` : String path to save output video


### Test example:
To preprocess the video: <br/>
`>>> python preprocessing.py -path_to "test_folder" -path_from "test.avi"` <br/>

To train: <br/>
`>>> python Main.py -train -path "test_folder"`<br/>
To test:<br/>
`>>> python Main.py -path "test_folder" -save_path "test_output/test.avi"`

*Note: That the folders passed in the above commands need to be created and should be empty*



