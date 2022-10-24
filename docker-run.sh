#!/bin/bash

python3 eva/eva_server.py &
# wait for server to start
sleep 30
python3 eva/eva_cmd_client.py