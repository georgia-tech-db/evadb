#!/bin/sh

# Run linter (checks code style)
flake8 --select E,F src/ test/ --exclude src/filters,src/parser/evaql
exit_code=$?
# Run unit tests
PYTHONPATH=./ pytest test/ --cov-report= --cov-config=.coveragerc --cov=src/ -s -v --log-level=10

if [ $exit_code -ne 0 ]; 
then 
    exit $exit_code 
else 
    exit 0 
fi
