# UA-DETRAC Dataset

### Table of Contents
* What is UA-DETRAC?
* How to Download and Unzip?
* How to format for inputting to Pytorch?

### What is UA-DETRAC?
* [UA-DETRAC Website](http://detrac-db.rit.albany.edu/home) contains description, video sample with annotations, benchmark, and annotation categories
* Multi-object tracking and detection dataset
* 10 hours of video at 24 locations in Beijing an Tianjin in China
* Recorded at __25 frames per second__
* Resolution is __960 x 540 pixels__
* More than __140 thousand frames__
* __8250 vehicles__ that are manually annotated
* Vehicle categories are __Car, Bus, Van,__ and __Other__
* Weather categories are __Night, Sunny, Rainy,__ and __Cloudy__
* Other annotations include __Scale of Vehicle, Occulsion Ratio,__ and __Truncation Ratio__. 



### How to Download and Unzip?


To Download all related files, navigate to Data directory and run download.sh

`bash download.sh`

To unzip all related files, in that directory, run unzip.sh

`bash unzip.sh`


Optionally, you can choose to download and unzip manually 

__UA-DETRAC training set__

`wget https://detrac-db.rit.albany.edu/Data/DETRAC-train-data.zip`

__UA-DETRAC test set__

`wget https://detrac-db.rit.albany.edu/Data/DETRAC-test-data.zip`

__Annotations regarding attribute information (e.g. vehicle category, weather, scale) used for detection training__

`wget https://drive.google.com/drive/folders/1FJfBiR7SPbMrOoPXfGDJjmV5qepXFsJy?usp=sharing/DETRAC-Train-Annotations-XML.zip -o DETRAC-Train_Annotations-XML.zip`

__Position information of target trajectories out of the general background, which is used for tracking and detection evaluation__

`wget https://drive.google.com/drive/folders/1FJfBiR7SPbMrOoPXfGDJjmV5qepXFsJy?usp=sharing/DETRAC-Train-Annotations-MAT.zip -o DETRAC-Train_Annotations-MAT.zip`


__Unzipping the dataset__

You can use your own method for unzipping .zip files or for conveniency

`sudo apt-get install unzip`

Now with unzip installed, you can easily unzip through command-line.

Example command would be 

`unzip DETRAC-train-data.zip`






