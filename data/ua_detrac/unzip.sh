#!/usr/bin/env bash

apt-get install unzip
unzip DETRAC-train-data.zip
unzip DETRAC-test-data.zip
unzip DETRAC-Train_Annotations-MAT.zip
unzip DETRAC-Train_Annotations-XML.zip

rm DETRAC-train-data.zip
rm DETRAC-test-data.zip
rm DETRAC-Train_Annotations-MAT.zip
rm DETRAC-Train_Annotations-XML.zip
