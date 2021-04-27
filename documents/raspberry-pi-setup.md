# Raspberry PI Setup

This document provides a guide to set up a Raspberry Pi with the Real Stereo Application.

## Prepare operating system

1. Download the [Raspberry Pi Imager](https://www.raspberrypi.org/software/) and open it
1. Choose OS: Raspberry Pi OS **(other)** -> Raspberry Pi OS **Lite**
1. Choose Storage: Select an available SD card (content will be overwritten)
1. Click on `Write` and wait until completion

## Installation

1. Insert the SD card into the Raspberry Pi and boot it
1. Login with user `pi` and password `raspberry` (note that the keyboard layout might have switched the `y` and `z` key)
1. (optional) To change the keyboard layout, run `sudo raspi-config` -> `5 Localisation Options` -> `L3 Keyboard`
1. Connect the Raspberry Pi to the internet with an ethernet cable
1. Run the install script by executing: `curl -sSL https://raw.githubusercontent.com/ItsEcholot/real-stereo-extended/main/scripts/pi-install.sh | bash -`
1. When the installation has finished, the Raspberry Pi will restart and is ready to use. The real stereo application will start automatically and listens on port `8080`.

### Optimizing OpenCV

It is possible to build opencv optimized for a raspberry pi which results in up to 200% better performance.
To do so, simply run `/home/pi/real-stereo-extended/scripts/pi-optimize-opencv.sh`.
The whole process can take up to 2 hours.

### Wifi setup

Until the feature has been implement into real stereo that the web interface provides a way to connect to a wifi network, you have to do it manually.

To do so, simply run `sudo raspi-config` -> `1 System Options` -> `S1 Wireless LAN`

### SSH

For development, an ssh server is started automatically.
To make deploying changes easier, it is suggested to add your public ssh key to the `~/.ssh/authorized_keys` file.
