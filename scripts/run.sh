#!/bin/bash
set -e

VERSION=$1
TYPE=${2:-cpu}

if [ "$TYPE" == "gpu" ]; then
    docker run --gpus all -it py:$VERSION-gpu /bin/bash
else
    docker run -it py:$VERSION-cpu /bin/bash
fi