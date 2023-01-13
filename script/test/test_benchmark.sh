#!/bin/sh

# generates a report for tests marked as benchmark tests

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
if [ -e ".benchmarks" ];
then
    echo "SUBSEQUENT RUN"
    # SUBSEQUENT RUNS
    PYTHONPATH=./ pytest test/  --benchmark-autosave --benchmark-compare  -s -v --benchmark-compare-fail=min:5% --log-level=WARNING ${1:-} -m "benchmark"
    test_code=$?
    if [ $test_code -ne 0 ];
    then
        exit $test_code
    fi
else
    echo "FIRST RUN"
    # FIRST RUN FOR REFERENCE
    PYTHONPATH=./ pytest test/  --benchmark-autosave -s -v --log-level=WARNING ${1:-} -m "benchmark"
    test_code=$?
    if [ $test_code -ne 0 ];
    then
        exit $test_code
    fi
fi

# restore __init__.py if it exists
if [ -f ./__init__.py.bak ]; then
    mv ./__init__.py.bak ./__init__.py
fi
