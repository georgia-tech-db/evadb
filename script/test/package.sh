#!/bin/bash

## Test package installation

function is_server_up () {
    # check if server started
    grep "serving" eva.txt
    return test_code
}

eva_server &>> eva.txt &
while [ $i -lt 3 ];
do
    sleep 20
    is_server_up
    test_code=$?
    if [ $test_code == 0 ]; then
        break
    fi
done

echo "Contents of server log"
cat eva.txt

if [ $test_code -ne 0 ];
then
    echo "Server did not start"
    echo $test_code
    exit $test_code
fi

eva_client &> client.txt &
if [ $test_code -ne 0 ];
then
    echo "Client did not start"
    echo $test_code
    exit $test_code
fi

head -n20 client.txt
exit 0
