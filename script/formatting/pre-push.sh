#!/bin/sh
echo "Linting code before commiting changes"
echo "Running script/formatting/formatter.py"
python script/formatting/formatter.py
exit_status=$?
if [ $exit_status -ne 0 ]; then
    echo "Oops! linting failed."
    echo "Please make sure 'python script/formatting/formatter.py' executes without error before committing."
    echo "In case you want to force commit, use the '--no-verify' flag while commiting."
    exit 1
fi

if git diff-index --quiet HEAD --; then
    echo "Code was reformatted. Please verify and stage the changes."
    echo "List of files updated."
    git --no-pager diff --name-only
    exit 1
fi

