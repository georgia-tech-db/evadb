#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
rm -rf $DIR/../../eva_datasets

mysql -u root -e 'Drop DATABASE eva_catalog;'
mysql -u root -e 'CREATE DATABASE IF NOT EXISTS eva_catalog;'
