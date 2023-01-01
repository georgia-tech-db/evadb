#!/bin/sh

# This script should return a non-zero value if either
# linter fails or the pytest fails. This is important for the CI system.

# temporarily remove __init__.py from root if it exists
if [ -f ./__init__.py ]; then
   mv ./__init__.py ./__init__.py.bak
fi

echo "OSTYPE: --|${OSTYPE}|--"
if [[ "$OSTYPE" != "msys" ]];
then 
    # Run black, isort, linter 
    sh script/formatting/pre-push.sh
    formatter_code=$?
    if [ $formatter_code -ne 0 ];
    then
        echo "FORMATTER CODE: --|${formatter_code}|-- FAILURE"
        exit $formatter_code
    else 
        echo "FORMATTER CODE: --|${formatter_code}|-- SUCCESS"
    fi
fi


# Keeping the duplicate linting for time being
# Run linter (checks code style)
PYTHONPATH=./ python -m flake8 --config=.flake8 eva/ test/ 
linter_code=$?

if [ "$linter_code" != "0" ];
then
    echo "FLAKE CODE: --|${linter_code}|-- FAILURE"
    exit $linter_code
else
    echo "FLAKE CODE: --|${linter_code}|-- SUCCESS"
fi


# Run unit tests
PYTHONPATH=./ python -m pytest test/utils --cov-report term --cov-config=.coveragerc --cov=eva/ -s -v --log-level=WARNING ${1:-} -m "not benchmark"
test_code=$?
if [ "$test_code" != "0" ];
then
    echo "PYTEST CODE: --|${test_code}|-- FAILURE"
    exit $test_code
else
    echo "PYTEST CODE: --|${test_code}|-- SUCCESS"
fi

# Run notebooks
PYTHONPATH=./ python -m pytest --nbmake --overwrite "./tutorials" -s -v --log-level=WARNING
notebook_test_code=$?
if [ "$notebook_test_code" != "0" ];
then
    cat tutorials/eva.log
    echo "NOTEBOOK CODE: --|${notebook_test_code}|-- FAILURE"
    exit $notebook_test_code
else
    echo "NOTEBOOK CODE: --|${notebook_test_code}|-- SUCCESS"
    # Success
    exit 0
fi

# restore __init__.py if it exists
if [ -f ./__init__.py.bak ]; then
    mv ./__init__.py.bak ./__init__.py
fi
