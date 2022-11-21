!/bin/sh

eva_server &> eva.txt &
sleep 3
head -n20 eva.txt
grep "serving" eva.txt || exit 255
eva_client &> client.txt &
head -n20 client.txt
