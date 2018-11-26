#Downloading the repo:

1. Use https://github.com/jwyang/faster-rcnn.pytorch to clone the repo. Download all the required data files.

#Running the FRCNN on a custom dataset (UADETRAC for this example)

1. After downloading the dataset unzip all the train, test and annotations files.
2. Go to faster_rcnn_pytorch/data/VOCDevkit2007/VOC2007 and replace all the contents with the unzipped train, test and 
annotation files.
3.Then I created a new pascal_voc file and made the following changes: i)Change the classes in the dataset background
should always be the first class. ii) Image set index should map to a directory that contains the names of the folders
that are present in the dataset. For example the Annotations folder consists of xml files where each xml file's name
corresponds to the folder names in INSIGHT-MVT-Train.
4. Had to make changes to _get_default_path and image_path_from_index the latter function points to which folder to
access in the train set so that we can extract the corresponding annotations from the xmk files.
5. Had to create a load_UADETRAC_annotation function to parse the annotations xml files to return the corresponding
ground truth labels and the bounding boxes for each image in the corresponding train folder.
6. In lib/datasets/factor.py replace make sure you replace PASCAL_VOC with the name of the class to the name you used
for the new pascal_voc. Replace all instances of the old class with the new class.
7. Finally to train the model run: CUDA_VISIBLE_DEVICES=$GPU_ID python trainval_net.py \
                   --dataset pascal_voc --net vgg16 \
                   --bs $BATCH_SIZE --nw $WORKER_NUMBER\
                   --cuda
    The command is available in the ReadMe of the original FasterRCNN cloned repo.
    

#Testing the trained models.

1. The trained model will be saved in the models folder followed by the name of DNN architecture used in the above case
it was vgg16 followed by the name of the dataset which is pascal_voc. Therefore the path is faster_rcnn_pytorch/models/vgg16/pascal_voc.

2.The demo.py file should be used to run the FRCNN on a set of images. The only change that would need to be made for a new 
dataset is to change the classes in the pascal_classes variable. 

3.python demo.py --net vgg16 \
               --checksession $SESSION --checkepoch $EPOCH --checkpoint $CHECKPOINT \
               --cuda --load_dir path/to/model/directoy
   Use this command to run the frcnn session,epoch,checkpoint correspond to the 3 numbers at the end of the stored model
   weights. --load_dir corresponds to the name of the directory that contains the test images. 
   The images containing detections are stored in the same path as load_dir but with the suffix _det.jpg.
   

#Running the FRCNN along with the PP and Color detection.

1. In the filters folder the file filter.py contains a function called pass_to_udf the arguments of the function are the predictions
by the chosen pp for the dataset/images and the corresponding images for which the predictions are made.

2.demo.py contains a function called accept_input_from_pp which accepts an array/list/tensor of images.

3.The evaluate_inp_from_pp function in demo.py gives the class, bounding boxes for these images and then creates an instance of
the TaskManager Class. The task manager class passes on the results to color_detection, vehichle_tracking, or speed.

4. The TaskManager Class is present in the filters folder. It accepts images,image bounding box,image class lists as input 
along with a string indicating the task="color"/"speed"/"in_out".


#Performance Measure

1. UDF

|Number of Images|Seconds
|       1        | 40.738
|       10       | 265.968

UDF Load time : 10.593


2.Color Detection
|Number of Bounding Boxes| Seconds
|           1            | 1.16 * 10^-5
|           5            | 2.36 * 10^-5 (on average)
