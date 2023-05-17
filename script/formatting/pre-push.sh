#!/bin/sh
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
NC='\033[0m'              # No Color

echo "Linting code before commiting changes"
echo "Running script/formatting/formatter.py"
python script/formatting/formatter.py
exit_status=$?
if [ $exit_status -ne 0 ]; then
    echo " ${Red}Oops! linting failed."
    echo " exit_status: ${exit_status}"
    echo "Please make sure 'python script/formatting/formatter.py' executes without error before committing."
    echo "In case you want to force push, use the '--no-verify' flag while commiting.${NC}"
    exit 1
fi

if ! git diff-index --quiet HEAD -- ':!./script/formatting/spelling.txt'; then
    echo "Code was reformatted or you have unstaged changes." 
    echo "Please verify and stage the changes."
    echo "List of files updated."
    git --no-pager diff --name-only
    exit 1
fi

