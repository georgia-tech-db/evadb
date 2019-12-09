

# Eva Storage Module README

### The storage module provides end to end help reducing the input datasize for fast video analytics.

*Note a GPU is required for using this module*

#### Functionality within this module:
1. Using a pre-trained model on the UE-DETRAC Dataset to get compressed clustered representations.
2. Training the model on your own data to get a latent representation optimized for your own input video.


#### Primary Outputs:
- `_.avi` compressed video in mp4 version. Can be used to extract representative frames within the video dataset.

#### Secondary Outputs:
`_.npy` encoded video file of representative frames <br/>
`_.pwf` new model file if model is trained<br/>
`_.avi` rescaled original video if scale is chosen or recovered video from CBIR if CBIR flag is chosen<br/>

## Usage:

##### Use the `download_files.sh` to download the pretrained model file and testing video

### Main.py

Main functionality can be browsed with the help command:

`>>> python Main.py -h`


Main function has the following inputs: <br/>
`-train` = boolean flag indicator model is to be to be retrained  <br/>
`-DETRAC` = boolean flag indicator if using the UE DETRAC dataset  <br/>
`-path` = string path to original video  <br/>
`-save_original_path` = path to where to save scale orginnal video  <br/>
`-cbir` = wherether or not to reprocude the recovered video for CBIR  <br/>
`-save_cbir_path` = path to save the recovered video   <br/>
`-save_compressed_path` = path to save the compressed  <br/>
`-scale` = scale to resize the original video <br/>
`-width` = width to reduce the original video to <br/>
`-height` = height to erduce the original video to <br/>
`-verbose` = boolean flag to print loss during training  <br/>
`-save_codec` = boolean flag to save the compressed codec <br/>


### Testing
We have defined a few explicit tests: <br/>

To re-train the network on a new video use the following command:  <br/>
`>>> python Main.py -path 'test.avi' -train -verbose`

Output would overwrite the existing model file <br/>

To compress a video at the original resolution:   <br/>
`>>> python Main.py -path 'test.avi' -save_compressed_path 'comp.avi'`

Output would return a compressed video that will look like a sped-up version of
the original input video. <br/>

To test query frames for CBIR reconstruction of original video: <br/>
`>>>python Main.py -path 'test.avi' -save_cbir_path 'cbir.avi' -cbir`

Output would be a clip which is compiled from the relevants frames of the original video <br/>

For recovery function the indexed frames have been hard coded for the above
test to be possible. Within the Eva infrastructure the frame information would
live as database meta data for frames and videos. <br/>


*Note: That the folders passed in the above commands need to be created and should be empty* <br/>



For any questions or concers please feel free to reach out to the authors at:<br/>
- kgeorge37@gatech.edu - Kevin George
- mike.groff@gatech.edu - Michael Groff
- amlk@gatech.edu - Ali Lakdawala

