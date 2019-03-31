## Hello readers!

### Installation
1. clone the Eva repository
2. checkout the Eva-storage branch. Although you might need to Google for the correct command, it will be something like

`$git checkout remote/Eva-storage`
3. navigate to eva/others/jupyter
4. Create conda environment (I have already composed an yaml file that you can directly use to create the environment)

`$conda env create -f <environment-name>.yml`
5. Details to the Convolutional AutoEncoders are in the file CAE_detrac.ipynb file. Specifically it contains the *CAE network* we will be using, and how to *load images from ua_detrac*
6. For compression and indexing, we will probably not need to parse the annotations, however, if this is needed, these functions are in  eva/loaders/load.py (_load_XML.py)
7. If you want to try out techniques with MNIST instead, the related loading functions are in  cluster prototype.ipynb

Happy Coding:)
