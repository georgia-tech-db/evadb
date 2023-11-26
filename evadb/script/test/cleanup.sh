#!/bin/bash

read -p "Remove the directory evadb_data/* [Y/n]?" yn
case $yn in
	[Yy]* ) rm -rf evadb_data/*;;
        * ) exit;;
esac
