#!/bin/bash

## Test package installation

function is_server_up () {
    # check if server started
    netstat -an | grep 0.0.0.0:5432
    return $?
}

eva_server &> eva.log &
SERVER_PID=$!
i=0
while [ $i -lt 5 ];
do
    echo "Waiting for server to launch, try $i"
    sleep 20
    is_server_up
    test_code=$?
    if [ $test_code == 0 ]; then
        break
    fi
    i=$((i+1))
done

echo "Contents of server log"
cat eva.log

if [ "$test_code" -ne 0 ];
then
    echo "Server did not start"
    echo "$test_code"
    exit "$test_code"
fi

cmd="exit"
echo "$cmd"  | eva_client &> client.log &

# wait for client to launch
sleep 5

# shutdown server
kill $SERVER_PID

echo "Contents of client log"
cat client.log

grep "failed" client.log
if [ "$?" -ne 1 ];
then
    echo "Client did not start"
    echo "$test_code"
    exit "$test_code"
fi

exit 0
