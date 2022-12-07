###############################
### EVA PACKAGAGING
###############################

import io
import os
import re

# to read contents of README file
from pathlib import Path
from typing import Dict

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

DESCRIPTION = "EVA Video Database System (Think MySQL for videos)."
NAME = "evadb"
AUTHOR = "Georgia Tech Database Group"
AUTHOR_EMAIL = "georgia.tech.db@gmail.com"
URL = "https://github.com/georgia-tech-db/eva"


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


# version.py defines the VERSION and VERSION_SHORT variables
VERSION_DICT: Dict[str, str] = {}
with open("eva/version.py", "r") as version_file:
    exec(version_file.read(), VERSION_DICT)

DOWNLOAD_URL = "https://github.com/georgia-tech-db/eva"
LICENSE = "Apache License 2.0"
VERSION = VERSION_DICT["VERSION"]

minimal_requirement = [
    "numpy>=1.19.5",
    "opencv-python>=4.5.4.60,!=4.6.0.66", # bug in easyocr
    "pandas>=1.1.5",
    "Pillow>=8.4.0",
    "sqlalchemy==1.3.20",
    "sqlalchemy-utils>=0.36.6",
    "antlr4-python3-runtime==4.8",
    "lark>=1.0.0",
    "pyyaml>=5.1,<5.2",
    "importlib-metadata<5.0",
    "ray>=1.13.0"    
]

formatter_libs = [
    "black>=22.6.0", 
    "isort>=5.10.1"
]

test_libs = [
    "pytest>=6.1.2",
    "pytest-cov>=2.11.1",
    "pytest-virtualenv",
    "coveralls>=3.0.1",
    "mock>=4.0.3",
    "flake8>=3.9.1"
]

notebook_libs = [
    "ipywidgets>=7.7.2",
    "matplotlib>=3.3.4",
    "nbmake>=1.2.1",
    "nest-asyncio>=1.5.6"
]

### NEEDED FOR INTEGRATION TESTS ONLY
integration_test_libs = [
    "torch>=1.10.0",
    "torchvision>=0.11.1",    
]

benchmark_libs = [
]

doc_libs = [
]

dist_libs = [
    "wheel>=0.37.1",
    "scriv>=0.16.0"
]

### NEEDED FOR AN ALTERNATE DATA SYSTEM OTHER THAN SQLITE
database_libs = [
    "pymysql>=0.10.1"
]

### NEEDED FOR A BATTERIES-LOADED EXPERIENCE
udf_libs = [
    "facenet-pytorch>=2.5.2",
    "easyocr>=1.5.0"
]

### NEEDED FOR EXPERIMENTAL FEATURES
experimental_libs = [
]

INSTALL_REQUIRES = minimal_requirement + integration_test_libs + udf_libs
DEV_REQUIRES = (
    INSTALL_REQUIRES
    + formatter_libs
    + test_libs
    + notebook_libs
    + benchmark_libs
    + doc_libs
    + database_libs
    + dist_libs
    + experimental_libs
) 

EXTRA_REQUIRES = {
    "dev": DEV_REQUIRES
}

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(exclude=[
        "tests", 
        "tests.*"
    ]),
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    entry_points={"console_scripts": [
        "eva_server=eva.eva_server:main",
        "eva_client=eva.eva_cmd_client:main"
    ]},
    python_requires=">=3.7",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    include_package_data=True,
    package_data={"eva": ["eva.yml"]}
)