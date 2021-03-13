#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$DIR"

# compile protobuf messages
protoc -I="$DIR/src" --python_out="$DIR/src/" "$DIR/src/protocol/cluster.proto"

# install python dependencies
poetry install
