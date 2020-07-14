#!/bin/sh

# This script should return a non-zero value if either
# linter fails or the pytest fails. This is important for the Travis.

# Run linter (checks code style)
flake8 --select E,F src/ test/ --exclude src/filters,src/parser/evaql
exit_code=$?
# Run unit tests
PYTHONPATH=./ pytest test/ --cov-report= --cov-config=.coveragerc --cov=src/ -s -v --log-level=10

if [ $exit_code -ne 0 ];
then
    exit $exit_code
else
    exit $?
fi
