#!/bin/sh

# This script should return a non-zero value if either
# linter fails or the pytest fails. This is important for the Travis.

# Run linter (checks code style)
flake8 --select E,F eva/ test/ --exclude src/filters,src/parser/evaql
linter_code=$?
# Run unit tests
PYTHONPATH=./ pytest test/ --cov-report= --cov-config=.coveragerc --cov=src/ -s -v --log-level=WARNING
test_code=$?
if [ $linter_code -ne 0 ];
then
    exit $linter_code
else
    exit $test_code
fi
