#!/bin/sh

# Install mysql and start server
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql

# Install java8 (for running antlr4)
sudo apt install openjdk-8-jdk openjdk-8-jre

# Install conda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a

# Install conda packages
conda env create -f environment.yml
source activate eva
conda list

# Create eva-catalog database
mysql -e 'CREATE DATABASE IF NOT EXISTS eva_catalog;'

# Generate eva-ql parser using antlr4
sh ./script/antlr4/setup.sh


 
