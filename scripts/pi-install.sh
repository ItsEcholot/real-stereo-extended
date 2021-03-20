#!/bin/bash

set -e

PROJECT_DIR="$HOME/real-stereo-extended"
PROJECT_GIT="https://github.com/ItsEcholot/real-stereo-extended.git"
PROJECT_BRANCH="main"

# update packages and distribution
sudo apt-get update
sudo apt-get dist-upgrade --yes

# add nodejs repository
curl -sL https://deb.nodesource.com/setup_14.x | sudo bash -

# install dependencies
sudo apt-get install --yes \
  build-essential \
  cmake \
  gfortran \
  git \
  libatlas-base-dev \
  libhdf5-103 \
  libhdf5-dev \
  libhdf5-serial-dev \
  libssl-dev \
  nodejs \
  pkg-config \
  protobuf-compiler \
  python-opencv \
  python3-apt \
  python3-dev \
  python3-distutils \
  python3-pip \
  python3-protobuf

# set up python
if [[ ! $(python --version | grep 'Python 3.') ]]; then
  sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
fi
if [[ ! -d "$HOME/.poetry" ]]; then
  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
fi
source "$HOME/.profile"

# set up node
sudo npm install --global yarn

# set up real stereo
if [[ ! -d "$PROJECT_DIR" ]]; then
  git clone $PROJECT_GIT $PROJECT_DIR
  (cd "$PROJECT_DIR" && git checkout $PROJECT_BRANCH)
else
  (cd "$PROJECT_DIR" && git pull)
fi
bash "$PROJECT_DIR/backend/install.sh" --pip
(cd "$PROJECT_DIR/frontend" && yarn install && yarn run build)
if [[ ! -f "/etc/systemd/system/real-stereo.service" ]]; then
  sudo ln -s "$PROJECT_DIR/scripts/config/real-stereo.service" /etc/systemd/system/real-stereo.service
fi
sudo systemctl enable real-stereo
sudo systemctl start real-stereo

# set up wifi
if [[ ! $(sudo cat /etc/wpa_supplicant/wpa_supplicant.conf | grep 'country') ]]; then
  sudo cp $PROJECT_DIR/scripts/config/wpa_supplicant.conf /boot/wpa_supplicant.conf
  sudo rfkill unblock wifi
  sudo ifconfig wlan0 up
fi

# set up ssh
if [[ ! -d "$HOME/.ssh" ]]; then
  sudo systemctl enable ssh
  sudo systemctl start ssh
  mkdir "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  touch "$HOME/.ssh/authorized_keys"
  chmod 600 "$HOME/.ssh/authorized_keys"
fi

# change the hostname
if [[ $(hostname) == 'raspberrypi' ]]; then
  echo "rse-$(hexdump -n 8 -e '4/4 "%08X" 1 "\n"' /dev/random)" | sudo dd of=/etc/hostname
fi

# reboot to apply all config changes
sudo shutdown -r now
