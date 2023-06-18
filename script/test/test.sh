#!/bin/bash

MODE=""                                   # Mode for testing
usage() {                                 # Function: Print a help message.
  echo "Usage: $0 [ -m MODE ]"  
}
exit_abnormal() {                         # Function: Exit with error.
  usage
  exit 1 # Failure
}

MODE="ALL"

while getopts "m:" options; do            
  case "${options}" in                    # 
    m)                                    # If the option is m,
      MODE=${OPTARG}                      # set $MODE to specified value.
      ;;
    *)                                    # If unknown (any other) option:
      exit_abnormal                       # Exit abnormally.
      ;;
  esac
done

# This script should return a non-zero value if either
# linter fails or the pytest or the benchmark fails. 
# This is important for the CI system.

PYTHON_VERSION=`python -c 'import sys; version=sys.version_info[:3]; print("{0}.{1}".format(*version))'`

echo "OSTYPE: --|${OSTYPE}|--"
echo "PYTHON VERSION: --|${PYTHON_VERSION}|--"
echo "MODE: --|${MODE}|--"

##################################################
## LINTER TESTS
##################################################

if [[ ( "$OSTYPE" != "msys" ) && ( "$MODE" = "LINTER" || "$MODE" = "ALL" ) ]];
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

if [[ ( "$OSTYPE" != "msys" ) && ( "$MODE" = "LINTER" || "$MODE" = "ALL" ) ]];
then 
    # Keeping the duplicate linting for time being
    # Run linter (checks code style)
    PYTHONPATH=./ python -m flake8 --config=.flake8 evadb/ test/ 
    linter_code=$?

    if [ "$linter_code" != "0" ];
    then
        echo "FLAKE CODE: --|${linter_code}|-- FAILURE"
        exit $linter_code
    else
        echo "FLAKE CODE: --|${linter_code}|-- SUCCESS"
    fi
fi

##################################################
## UNIT TESTS
## with cov pytest plugin
##################################################

if [[ "$OSTYPE" != "msys" ]];
# Non-Windows
then
    if [[ "$MODE" = "TEST" || "$MODE" = "ALL" ]];
    then
        PYTHONPATH=./ pytest --durations=20 --capture=sys --tb=short -v --log-level=WARNING -rsf -p no:cov test/ -m "not benchmark"
    elif [[ "$MODE" = "COV" ]];
    then
	# As a workaround, ray needs to be disabled for COV.
        PYTHONPATH=./ pytest --durations=20 --cov-report term-missing:skip-covered  --cov-config=.coveragerc --cov-context=test --cov=evadb/ --capture=sys --tb=short -v -rsf --log-level=WARNING -m "not benchmark"
    fi

    test_code=$?
    if [ "$test_code" != "0" ];
    then
        echo "PYTEST CODE: --|${test_code}|-- FAILURE"
        exit $test_code
    else
        echo "PYTEST CODE: --|${test_code}|-- SUCCESS"
    fi
# Windows -- no need for coverage report
else
    PYTHONPATH=./ python -m pytest -p no:cov test/ -m "not benchmark"
    test_code=$?
    if [ "$test_code" != "0" ];
    then
        echo "PYTEST CODE: --|${test_code}|-- FAILURE"
    else
        echo "PYTEST CODE: --|${test_code}|-- SUCCESS"
    fi
fi

##################################################
## TEST JUPYTER NOTEBOOKS
## with nbmake pytest plugin
##################################################

if [[ ( "$OSTYPE" != "msys" ) && ( "$MODE" = "NOTEBOOK" || "$MODE" = "ALL" ) ]];
then 
    PYTHONPATH=./ python -m pytest --durations=5 --nbmake --overwrite "./tutorials" --capture=sys --tb=short -v --log-level=WARNING --nbmake-timeout=3000
    notebook_test_code=$?
    if [ "$notebook_test_code" != "0" ];
    then
        cat tutorials/evadb.log
        echo "NOTEBOOK CODE: --|${notebook_test_code}|-- FAILURE"
        exit $notebook_test_code
    else
        echo "NOTEBOOK CODE: --|${notebook_test_code}|-- SUCCESS"
    fi
fi

##################################################
## UPLOAD COVERAGE
## based on Python version
##################################################

if [[ ( "$PYTHON_VERSION" = "3.10" )  && 
      ( "$MODE" = "COV" ) ]];
then 
    echo "UPLOADING COVERAGE REPORT"
    coveralls
    exit 0 # Success     
fi
