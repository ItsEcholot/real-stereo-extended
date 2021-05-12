#!/bin/bash

set -e

# stopping real-stereo
sudo service real-stereo stop

# install dependencies
sudo apt-get install -y build-essential cmake pkg-config checkinstall \
  libjpeg-dev libpng-dev libtiff-dev libprotobuf-dev protobuf-compiler

# enlarge swap
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=2048/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

# remove opencv previously installed through pip
if [[ $(pip3 list | grep opencv) ]]; then
  pip3 uninstall -y opencv-python-headless
  pip3 uninstall -y numpy || true # fails if installed with apt-get, which is what we want so it can be ignored
  sudo apt-get install -y python3-numpy
fi

# clone TBB
git clone https://github.com/oneapi-src/oneTBB.git /home/pi/tbb
cd /home/pi/tbb
git checkout 9e15720bc7744f85dff611d34d65e9099e077da4
CXXFLAGS="-DTBB_USE_GCC_BUILTINS=1 -D__TBB_64BIT_ATOMICS=0" cmake -DTBB_TEST:BOOL=OFF --configure .
CXXFLAGS="-DTBB_USE_GCC_BUILTINS=1 -D__TBB_64BIT_ATOMICS=0" cmake --build .
sudo cmake -DCOMPONENT=runtime -P cmake_install.cmake
sudo cmake -DCOMPONENT=devel -P cmake_install.cmake

# clone opencv
git clone --depth 1 https://github.com/opencv/opencv.git /home/pi/opencv
mkdir /home/pi/opencv/build
cd /home/pi/opencv/build

# compile opencv
export CFLAGS="-mcpu=cortex-a53 -mfloat-abi=hard -mfpu=neon-fp-armv8 -mneon-for-64bits -DTBB_USE_GCC_BUILTINS=1 -D__TBB_64BIT_ATOMICS=0"
export CXXFLAGS="-mcpu=cortex-a53 -mfloat-abi=hard -mfpu=neon-fp-armv8 -mneon-for-64bits -DTBB_USE_GCC_BUILTINS=1 -D__TBB_64BIT_ATOMICS=0"

cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
-D BUILD_opencv_python2=OFF \
-D BUILD_opencv_python3=ON \
-D WITH_TBB=ON \
-D WITH_OPENMP=ON \
-D ENABLE_NEON=ON \
-D ENABLE_VFPV3=ON \
-D BUILD_TESTS=OFF \
-D INSTALL_PYTHON_EXAMPLES=OFF \
-D OPENCV_ENABLE_NONFREE=OFF \
-D OPENCV_EXTRA_EXE_LINKER_FLAGS=-latomic \
-D BUILD_PERF_TESTS=OFF \
-D BUILD_EXAMPLES=OFF ..

make
sudo make install
sudo ldconfig

# shrink swap again
sudo sed -i 's/CONF_SWAPSIZE=2048/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

# start real-stereo again
sudo service real-stereo start
