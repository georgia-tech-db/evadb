#!/bin/sh

# This script should return a non-zero value if either
# linter fails or the pytest fails. This is important for the CI system.

# temporarily remove __init__.py from root if it exists
if [ -f ./__init__.py ]; then
   mv ./__init__.py ./__init__.py.bak
fi

# Run black, isort, linter 
sh script/formatting/pre-push.sh
return_code=$?
if [ $return_code -ne 0 ];
then
    exit $return_code
fi

# Keeping the duplicate linting for time being
# Run linter (checks code style)
python -m flake8 --config=.flake8 eva/ test/
linter_code=$?

if [ $linter_code -ne 0 ];
then
    exit $linter_code
fi


# Run unit tests
PYTHONPATH=./ python -m pytest test/ --cov-report term --cov-config=.coveragerc --cov=eva/ -s -v --log-level=WARNING ${1:-} -m "not benchmark"
test_code=$?
if [ $test_code -ne 0 ];
then
    exit $test_code
fi

# Run notebooks
PYTHONPATH=./ python -m pytest --nbmake --overwrite "./tutorials" -s -v --log-level=WARNING
notebook_test_code=$?
if [ $notebook_test_code -ne 0 ];
then
    cat tutorials/eva.log
    exit $notebook_test_code
else
    exit 0
fi

# restore __init__.py if it exists
if [ -f ./__init__.py.bak ]; then
    mv ./__init__.py.bak ./__init__.py
fi
