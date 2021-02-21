#!/bin/sh

# Install mysql and start server
sudo -E apt-get update
sudo -E apt-get -q -y install mysql-server
sudo systemctl start mysql

# Install java8 (for running antlr4)
sudo -E apt install -y openjdk-8-jdk openjdk-8-jre

# Install conda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a

