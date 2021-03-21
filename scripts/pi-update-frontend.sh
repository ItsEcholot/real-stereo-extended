#!/bin/bash

IP="$1"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [[ -z $IP ]]; then
  echo "Usage: $0 <ip-address>"
  exit 1
fi

rm -f "$DIR/.change.log"
rsync --recursive --links --times --perms --devices --specials --delete --compress --verbose --log-file="$DIR/.change.log" --log-file-format="file-change: %f %i" --exclude "*/node_modules/" --exclude "/node_modules/*" --exclude "*/node_modules/*" --exclude "*/build/" --exclude "build/*" --exclude "*/build/*" "$DIR/../frontend/" "pi@$IP:/home/pi/real-stereo-extended/frontend"

# check if the dependencies have changed and updated them if so
if [[ $(grep 'file-change:.*yarn.lock' "$DIR/.change.log") ]]; then
  echo ""
  echo "Dependencies have changed, updating..."
  ssh "pi@$IP" 'source ~/.profile && cd ~/real-stereo-extended/frontend && yarn install'
fi
rm -f "$DIR/.change.log"

# build the frontend
ssh -t "pi@$IP" "cd ~/real-stereo-extended/frontend && yarn build"
