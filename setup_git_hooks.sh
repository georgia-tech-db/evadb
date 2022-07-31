#!/bin/bash
chmod +x script/formatting/pre-push.sh
ln -s script/formatting/pre-push.sh .git/hooks/pre-push
