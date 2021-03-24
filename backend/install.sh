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

  # maually install picamera since that module fails if not installed on a pi
  pip3 install "picamera[array]"
else
  poetry install
fi
