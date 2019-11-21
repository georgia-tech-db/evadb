# **Depth Estimation using Deep learning**

Course project for CS 8803 - Data Analysis with Deep Learning at Georgia Institute of Technology.

### Contributors:

  1. pratrajv - Prateek Rajvanshi
  2. vaishnavik22 - Vaishnavi Kannan
  3. imvinod - Vinod Kumar
  4. jShay - Jhanavi Sanjay Sheth

### Problem Statement
1. The problem is about performing depth estimation of a scene during robot navigation
2. Intensive task that require significant execution time
3. Experiment on various pre processing techniques to reduce the execution time
4. Ensure that model performance is not impacted


### Why is this important?

1. Autonomous vehicles, warehouse robots, industrial mobile robots are being utilized in a scale larger than ever.
2. Perception plays a key role in enabling intelligent robots to sense the environment accurately.
3. Any technique that reduces processing time and results in an increase of number of frames per second works in favour of better perception.
4. Potential to directly impact how future robots perceive the world.

### Approach

1. Input image from a monocular (single) camera. Size of the input image is : 375 X 1242 X 3
2. Dimensionality reduction using PCA to reduce the size of the input image passed to the Depth Estimator model.
3. Spatial Frame filtering - We create a mask of the pixels we want to remove from the current frame and reduce the input image size before applying object detection.
4. DL Model Architecture: Has an encoder - decoder layer.
          Encoder: Convolution
          Decoder: Upsampling
5. Skipping depth estimate for frames: if difference in depth map less than threshold (hyperparameter), skip depth calculation 5. Output is a depth estimate of the input image having size 375 X 1242 X 1

### Dataset

Dataset used for this project is the Kitti dataset. Available for download at : http://www.cvlibs.net/datasets/kitti/

### Third party library
1. We have used pytorch in our model implementation
2. Pytest framework for unit tests
3. The Deep learning architecture is from the paper titled: Real-Time Joint Semantic Segmentation and Depth Estimation Using Asymmetric Annotations for non-commercial purposes.
Credits to the Author: Vladimir Nekrasov et al. (https://arxiv.org/abs/1809.04766)

### Execution
There are two approaches to execute the project.

#### Approach 1:
* This approach uses the code integrated with Eva repository. (https://github.com/jhanavi/Eva).
* Please note that currently entire code has not been integrated with Eva. And, hence there is no direct project execution file in this repository.
* You can run the project using pytest framework. The unit test itself calls the deep learning model for prediction.
* Once the integration with Eva is completed before final phase, there will be a main process file which will be responsible for project execution.
* For now, you just need to type pytest command from the root directory and it will execute all the unit tests.


#### Approach 2:
* This approach uses the code from previous checkpoint before we migrated to Eva repository. (https://github.com/imvinod/ddl_depth_estimation)
* Main file to simulate DL model - process.ipynb
* The python notebook simulates performance comparison of the DL model for all improvements done:
1. PCA
2. Frame skipping
3. Depth map projection

The notebook invokes functions implemented in the source python files.


### Code structure

We have followed the existing code hierarchy of Eva repository. No new hierarchy is added.

We have added our main file for processing the frames under /UDFs directory.
##### src/udfs/depth_estimator.py
UDF class for depth estimation feature. responsible for taking batch of frames.
It processes the frames, sends them to deep learning model for predictions.
Consolidates the model output and store them in DepthEstimationResult object.


##### src/udfs/abstract_udfs.py
This is existing abstract UDF class in eva repository.
We have updated this class to also extend a new method called process_frames which is implemented by depth_estimator class.


##### src/udfs/ExpKITTI_joint.ckpt
Model checkpoint file


We have added unit tests under the /test/udfs directory
##### test/udfs/test_depth_estimator.py
A class for implementing unit tests for depth estimator.


Data files for unit test are stored under /test/udfs/data directory
##### test/udfs/data/kitti_car_1.png
##### test/udfs/data/kitti_car_2.png


Under /src directory we have implemented a data model file  depth_estimation_result.py for storing depth estimation results.
#### src/depth_estimation_result.py



### TaskList

Completed:
* [x] Implementation of Deep learning model for depth Estimation. Trained DL model on kitti dataset
* [x] Implement frame skipping
* [x] Implement PCA for dimensionality reduction
* [x] Implement spatial frame filtering to reduce size of image passed to DL model

To do:
* [ ] Integrate Frame Filtering with Eva
* [ ] Enable depth estimation execution through Eva repository

