#!/bin/sh

# Install conda packages for eva
conda env create -f script/install/conda_eva_environment.yml
. activate eva
conda list

# Generate eva-ql parser using antlr4
sh script/antlr4/generate_parser.sh

