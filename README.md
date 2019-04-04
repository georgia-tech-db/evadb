## EVA (Exploratory Video Analytics)

### Table of Contents
* Installation
* Demos
* Eva core
* Eva storage 
* Dataset 


### Installation
* Clone the repo
* Create a virtual environment with conda (explained in detail in the next subsection)


##### How to create the virtual environment
* Install conda - we have prepared a yaml file that you can directly use with conda to install a virtual environment 
* Navigate to the eva repository in your local computer
* conda env create -f environment.yml
* Note, this yaml file should install and all code should run with no errors in Ubuntu 16.04.
   However, there are know installation issues with MacOS.
    
### Demos
We have demos for the following components:
1. Eva analytics (pipeline for loading the dataset, training the filters, and outputting the optimal plan)
```bash
   cd $YOUR_EVA_DIRECTORY
   python pipeline.py
```
2. Eva Query Optimizer (Will show converted queries for the original queries)
```bash
   cd $YOUR_EVA_DIRECTORY
   python query_optimizer/query_optimizer.py
```
3. Eva Loader (Loads UA-DETRAC dataset)
```bash
   cd $YOUR_EVA_DIRECTORY
   python loaders/load.py
```

2. EVA storage-system (Video compression and indexing system - *currently in progress*)

### Eva Core
Eva core is consisted of
* Query Optimizer
* Filters
* UDFs
* Loaders

##### Query Optimizer
The query optimizer converts a given query to the optimal form. 

All code related to this module is in */query_optimizer*

##### Filters
The filters does preliminary filtering to video frames using cheap machine learning models.
The filters module also outputs statistics such as reduction rate and cost that is used by Query Optimizer module.

The preprocessing method below is running:
* PCA

The filters below are running:
* KDE
* DNN
* Random Forest
* SVM

All code related to this module is in */filters*

##### UDFs
This module contains all imported deep learning models. Currently, there is no code that performs this task. It is a work in progress.
Information of current work is explained in detail [here](udfs/README.md).

All related code should be inside */udfs*

##### Loaders
The loaders load the dataset with the attributes specified in the *Accelerating Machine Learning Inference with Probabilistic Predicates* by Yao et al.

All code related to this module is in */loaders*

### Eva storage
Currently a work in progress. Come check back later!


### Dataset
__[Dataset info](data/README.md)__ explains detailed information about the  datasets




