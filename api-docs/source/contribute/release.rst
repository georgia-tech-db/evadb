Releasing
~~~~~~~~~~

These are steps involved in releasing a new version of EVA.

1. Generate EVA grammar files.

::

    bash script/antlr4/generate_parser.sh

Bump up version number in `version.py` along with any additional dependencies.

2. Create a new build locally. 

::

    python -m build 


3. Upload build to pypi using credentials.

::

    python -m twine upload dist/* 

