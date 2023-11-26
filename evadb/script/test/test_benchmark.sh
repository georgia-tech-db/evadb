#!/bin/sh

# generates a report for tests marked as benchmark tests

# temporarily remove __init__.py from root if it exists
if [ -f ./__init__.py ]; then
   mv ./__init__.py ./__init__.py.bak
fi

git log | head

# Run only benchmark tests
if [ -e ".benchmarks" ];
then
    echo "SUBSEQUENT RUN"
    # SUBSEQUENT RUNS
    PYTHONPATH=./ pytest test/  --benchmark-autosave --benchmark-compare --benchmark-columns="mean" --benchmark-group-by="name"  -v --benchmark-compare-fail=min:20%  ${1:-} -m "benchmark"
    test_code=$?
    if [ $test_code -ne 0 ];
    then
        exit $test_code
    fi
else
    echo "FIRST RUN"
    # FIRST RUN FOR REFERENCE
    PYTHONPATH=./ pytest test/  --benchmark-autosave --benchmark-columns="mean" -v ${1:-} -m "benchmark"
    test_code=$?
    if [ $test_code -ne 0 ];
    then
        exit $test_code
    fi
fi

# Check demo page
curl https://ada-00.cc.gatech.edu/evadb/playground
demo_code=$?
if [ $demo_code -ne 0 ];
then
    echo "Demo down!"
    exit $demo_code
fi

# restore __init__.py if it exists
if [ -f ./__init__.py.bak ]; then
    mv ./__init__.py.bak ./__init__.py
fi
