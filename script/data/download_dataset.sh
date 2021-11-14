#!/bin/sh

# path of the dataset folder
DATASET_NAME=$1
DATASET_PATH="../../data/datasets/"

# check if the datasets folder exists, if not create it
if [ ! -d "$DATASET_PATH" ]; then
    mkdir $DATASET_PATH$
fi

echo "Downloading dataset ${DATASET_NAME} into ${DATASET_PATH}"

# check if the dataset folder already exists
if [ -d "${DATASET_PATH}/${DATASET_NAME}" ]; then
    echo "Dataset folder already exists"
else
    # execute the python script to download the dataset
    python3 download_file.py $DATASET_NAME

    # unzip the dataset
    echo "Unzipping dataset"
    unzip -q $DATASET_NAME.zip -d $DATASET_PATH

    # remove the zip file
    echo "Removing zip file"
    rm $DATASET_NAME.zip
fi
