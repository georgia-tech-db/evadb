#!/bin/sh

# path of the model folder
MODEL_NAME=$1
MODEL_PATH="../../data/models/"

# check if the models folder exists, if not create it
if [ ! -d "$MODEL_PATH" ]; then
    mkdir $MODEL_PATH$
fi

echo "Downloading model ${MODEL_NAME} into ${MODEL_PATH}"

# check if the model folder already exists
if [ -d "${MODEL_PATH}/${MODEL_NAME}" ]; then
    echo "Dataset folder already exists"
else
    # execute the python script to download the model
    python3 download_file.py $MODEL_NAME

    # unzip the model
    echo "Unzipping dataset"
    unzip -q $MODEL_NAME.zip -d $MODEL_PATH

    # remove the zip file
    echo "Removing zip file"
    rm $MODEL_NAME.zip
fi
