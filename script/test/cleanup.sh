#!/bin/bash

read -p "Remove the directory ~/.eva/* [Y/n]?" yn
case $yn in
	[Yy]* ) rm -rf ~/.eva/*;;
        * ) exit;;
esac
