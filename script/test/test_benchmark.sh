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

# Run only benchmark tests
PYTHONPATH=./ pytest test/ --cov-report term --cov-config=.coveragerc --cov=eva/ -s -v --log-level=WARNING ${1:-} -m "benchmark"
test_code=$?
if [ $test_code -ne 0 ];
then
    exit $test_code
fi

# restore __init__.py if it exists
if [ -f ./__init__.py.bak ]; then
    mv ./__init__.py.bak ./__init__.py
fi
