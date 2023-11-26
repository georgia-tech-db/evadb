#!/bin/bash

## backward compatibility
EvaDB_VERSION=$(pip show evadb | grep Version | awk '{print $2}')
if [[ "$EvaDB_VERSION" < "0.2.4" ]]; then
    PORT=5432
else
    PORT=8803
fi

## Test package installation

function is_server_up () {
    # check if server started
    pgrep "evadb_server"
    status_code=$?
    echo $status_code
    return $status_code
}

evadb_server &> evadb.log &
SERVER_PID=$!
echo $SERVER_PID
i=0
while [ $i -lt 5 ];
do
    echo "Waiting for server to launch, try $i"
    sleep 5
    is_server_up
    test_code=$?
    if [ $test_code == 0 ]; then
        break
    fi
    i=$((i+1))
done

echo "Contents of server log"
cat evadb.log

if [ "$test_code" -ne 0 ];
then
    echo "Server did not start"
    echo "$test_code"
    cat evadb.log
    exit "$test_code"
fi

cmd="exit"
echo "$cmd"  | evadb_client &> client.log &

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
    cat client.log
    exit "$test_code"
fi

exit 0
