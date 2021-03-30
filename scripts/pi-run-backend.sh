#!/bin/bash

IP="$1"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [[ -z $IP ]]; then
  echo "Usage: $0 <ip-address>"
  exit 1
fi

# sync code
"$DIR/pi-update-backend.sh" $IP

# stop service if it is running
ssh "pi@$IP" 'if [[ $(sudo systemctl status real-stereo) ]]; then sudo systemctl stop real-stereo; fi'

# start real-stereo interactively
ssh -o ServerAliveInterval=240 -t "pi@$IP" "cd ~/real-stereo-extended/backend && python src ${@:2}"
