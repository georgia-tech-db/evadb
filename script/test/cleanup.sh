#!/bin/bash

USER=${1:-root}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
rm -rf $DIR/../../eva_datasets

mysql -u $USER -e 'Drop DATABASE eva_catalog;'
mysql -u $USER -e 'CREATE DATABASE IF NOT EXISTS eva_catalog;'
