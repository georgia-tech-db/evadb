#!/bin/bash
chmod +x script/formatting/pre-push.sh
ln -s "$PWD"/script/formatting/pre-push.sh .git/hooks/pre-push
