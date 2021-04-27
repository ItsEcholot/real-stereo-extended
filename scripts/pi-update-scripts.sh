#!/bin/bash

IP="$1"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [[ -z $IP ]]; then
  echo "Usage: $0 <ip-address>"
  exit 1
fi

rsync --recursive --links --times --perms --devices --specials --delete --compress --verbose "$DIR/../scripts/" "pi@$IP:/home/pi/real-stereo-extended/scripts"
