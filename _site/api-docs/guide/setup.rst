.. _guide-setup:

Setup
===========

Installation of EVA involves setting a virtual environment using `miniconda <https://conda.io/projects/conda/en/latest/user-guide/install/index.html>`_ and configuring git hooks.

- Clone the repository::

    git clone https://github.com/georgia-tech-db/eva.git

- Install the dependencies::

    sh script/install/before_install.sh
    export PATH="$HOME/miniconda/bin:$PATH"
    sh script/install/install.sh
