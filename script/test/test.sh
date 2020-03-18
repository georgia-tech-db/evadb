#!/bin/sh

# Activa eva environment
. activate eva

# Run linter (checks code style)
pycodestyle  --select E src/ test/ --exclude src/filters,src/parser/evaql

# Run unit tests
PYTHONPATH=./ pytest test/ --cov-report= --cov-config=.coveragerc --cov=src/ -s -v --log-level=10



