#!/bin/bash

IP="$1"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

if [[ -z $IP ]]; then
  echo "Usage: $0 <ip-address>"
  exit 1
fi

rm -f "$DIR/.change.log"
rsync --recursive --links --times --perms --devices --specials --delete --compress --verbose --log-file="$DIR/.change.log" --log-file-format="file-change: %f %i" --exclude "config.json" --exclude "certificate.crt" --exclude "certificate.key" --exclude "*/cluster_pb2.py" --exclude "*/__pycache__/" --exclude "/__pycache__/*" --exclude "*/__pycache__/*" --exclude "*/.venv/" --exclude ".venv/*" --exclude "*/.venv/*"  --exclude "*/custom_calibration.pkl" "$DIR/../backend/" "pi@$IP:/home/pi/real-stereo-extended/backend"

# check if the dependencies have changed and updated them if so
if [[ $(grep 'file-change:.*poetry.lock' "$DIR/.change.log") ]] || [[ $(grep 'file-change:.*cluster.proto' "$DIR/.change.log") ]]; then
  echo ""
  echo "Dependencies have changed, updating..."
  ssh "pi@$IP" 'source ~/.profile && ~/real-stereo-extended/backend/install.sh --pip'
fi
rm -f "$DIR/.change.log"
