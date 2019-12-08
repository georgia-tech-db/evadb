#!/bin/bash

rm -f data.zip

#fileid= "1YV6uirkTNMTnGMRrLoGYZPP1MmYLQhni"
#filename="ExpKITTI_joint.ckpt"
#url='https://docs.google.com/uc?export=download&id='$fileid
#wget -O $filename $url

wget -O ExpKITTI_joint.ckpt 'https://docs.google.com/uc?export=download&id=1YV6uirkTNMTnGMRrLoGYZPP1MmYLQhni'

wget -O data.zip 'https://docs.google.com/uc?export=download&id=1Wi5LzRASdlP76miEtXuAewmlaZly-pN3'
unzip data.zip
rm -f data.zip

exit 0

