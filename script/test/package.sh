!/bin/sh

eva_server &> eva.txt &
sleep 3
grep "serving" eva.txt || return -1
eva_client

