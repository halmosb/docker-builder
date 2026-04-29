#!/bin/bash
set -e

docker image prune -f

# remove project images
for img in $(docker images "py:*" -q); do
    docker rmi -f $img
    echo "Deleting $img"
done

for img in $(docker images "python:*" -q); do
    docker rmi -f $img
    echo "Deleting $img"
done

# Remove pulled images
for img in $(docker images "*/docker-builder/python:*" -q); do
    docker rmi -f $img
    echo "Deleting $img"
done