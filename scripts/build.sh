#!/bin/bash
set -e

PY_VERSIONS=("3.12" "3.13" "3.14")

for v in "${PY_VERSIONS[@]}"; do
    docker build -f generated/Dockerfile.cpu.$v -t py:$v-cpu .
    docker build -f generated/Dockerfile.gpu.$v -t py:$v-gpu .
done