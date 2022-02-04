
#!/bin/sh

# name of the datset
DATASET_NAME=$1

# get script path
SCRIPT_PATH=$(dirname $0)

echo "Loading dataset ${DATASET_NAME} into EVA"

# execute the python script
python $SCRIPT_PATH/load_dataset.py ${DATASET_NAME}