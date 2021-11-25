from setuptools import find_packages, setup

setup(
    packages=find_packages(exclude=("test*",)),
    python_requires=">=3.6",
    install_requires=[
        "numpy==1.20.1",
        "opencv-python==4.5.1.48",
        "pandas==1.2.3",
        "torch==1.7.1",
        "torchvision==0.8.2",
        "pillow",
        "sqlalchemy==1.3.20",
        "pymysql==0.10.1",
        "sqlalchemy-utils==0.36.6",
        "pytest-asyncio==0.14.0",
        "pyspark==3.0.2",
        "petastorm==0.9.8",
        "antlr4-python3-runtime==4.8",
        "pyyaml"
    ],
    entry_points={
        'console_scripts': [
            'eva_server=eva.eva_server:main',
            'eva_client=eva.eva_cmd_client:main'
        ],
    },
    package_data={
        "": ["*.yml", ],
    }
)
