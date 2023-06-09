###############################
### EvaDB PACKAGAGING
###############################

import io
import os

# to read contents of README file
from pathlib import Path
from typing import Dict

from setuptools import find_packages, setup
from setuptools.command.install import install
from subprocess import check_call

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

DESCRIPTION = "EvaDB AI-Relational Database System"
NAME = "evadb"
AUTHOR = "Georgia Tech Database Group"
AUTHOR_EMAIL = "arulraj@gatech.edu"
URL = "https://github.com/georgia-tech-db/eva"


def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


# version.py defines the VERSION and VERSION_SHORT variables
VERSION_DICT: Dict[str, str] = {}
with open("evadb/version.py", "r") as version_file:
    exec(version_file.read(), VERSION_DICT)

DOWNLOAD_URL = "https://github.com/georgia-tech-db/eva"
LICENSE = "Apache License 2.0"
VERSION = VERSION_DICT["VERSION"]

minimal_requirement = [
    "numpy>=1.19.5",
    "pandas>=1.1.5",
    "opencv-contrib-python-headless>=4.6.0.66",
    "Pillow>=8.4.0",
    "sqlalchemy>=1.4.0,<2.0.0",  # major changes in 2.0.0
    "sqlalchemy-utils>=0.36.6",
    "lark>=1.0.0",
    "pyyaml>=5.1",
    "importlib-metadata<5.0",
    "ray>=1.13.0,<2.5.0", # breaking change in 2.5.0
    "retry>=0.9.2",
    "aenum>=2.2.0",
    "diskcache>=5.4.0",
    "eva-decord>=0.6.1",
    "boto3",
    "nest_asyncio",
    "langchain",
    "pymupdf",
    "pdfminer.six",
    "sentence-transformers"

]

formatter_libs = ["black>=23.1.0", "isort>=5.10.1"]

test_libs = [
    "pytest>=6.1.2",
    "pytest-cov>=2.11.1",
    "pytest-random-order>=1.0.4",
    "pytest-virtualenv",
    "pytest-asyncio",
    "pytest-xdist",
    "coveralls>=3.0.1",
    "flake8>=3.9.1",
    "moto[s3]>=4.1.1",
]

notebook_libs = [
    "ipywidgets>=7.7.2",
    "matplotlib>=3.3.4",
    "nbmake>=1.2.1",
    "nest-asyncio>=1.5.6",
]

### NEEDED FOR INTEGRATION TESTS ONLY
integration_test_libs = [
    "torch>=1.10.0",
    "torchvision>=0.11.1",
    "faiss-cpu",  # faiss-gpu does not work on mac
]

benchmark_libs = [
    "pytest-benchmark",
]

doc_libs = ["codespell", "pylint"]

dist_libs = [
    "wheel>=0.37.1",
    "semantic_version",
    "PyGithub",
    "twine",
    "PyDriller"
]

### NEEDED FOR AN ALTERNATE DATA SYSTEM OTHER THAN SQLITE
database_libs = ["pymysql>=0.10.1"]

### NEEDED FOR A BATTERIES-LOADED EXPERIENCE
udf_libs = [
    "facenet-pytorch>=2.5.2",  # FACE DETECTION
    "ipython<8.13.0",  # NOTEBOOKS
    "thefuzz",  # FUZZY STRING MATCHING
    "ultralytics>=8.0.93",  # OBJECT DETECTION
    "transformers>=4.27.4",  # HUGGINGFACE
    "openai>=0.27.4",  # CHATGPT
    "retry>=0.9.2", #CHATGPT
    "timm>=0.6.13",  # HUGGINGFACE VISION TASKS
    "norfair>=2.2.0",  # OBJECT TRACKING
]

### NEEDED FOR EXPERIMENTAL FEATURES
third_party_libs = [
    "qdrant-client>=1.1.7",  # Qdrant vector store client
    "kornia",  # SIFT features
    "langchain>=0.0.177",  # langchain document loaders
    "pdfminer.six",  # for reading pdfs
]

### NEEDED FOR EXPERIMENTAL FEATURES
experimental_libs = []

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
    + third_party_libs
)

EXTRA_REQUIRES = {"dev": DEV_REQUIRES}

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
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        # "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    entry_points={
        "console_scripts": [
            "eva_server=evadb.evadb_server:main",
            "eva_client=evadb.evadb_cmd_client:main",
        ]
    },
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    include_package_data=True,
    package_data={"evadb": ["evadb.yml", "parser/evadb.lark"]},
)
