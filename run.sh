#!/bin/bash -e
fname=$(./slurp)
./post-process.py write-tag-cache --file "${fname}"
./post-process.py upload-pod --file "${fname}"
./post-process.py gen-feed
