#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$DIR"

# compile protobuf messages
protoc -I="$DIR/src" --python_out="$DIR/src/" "$DIR/src/protocol/cluster.proto"

# install python dependencies
if [[ "$1" == "--pip" ]]; then
  poetry export --format requirements.txt --output requirements.txt --without-hashes
  pip3 install -r requirements.txt
  rm requirements.txt
else
  poetry install
fi
