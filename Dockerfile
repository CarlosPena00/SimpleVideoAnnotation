# Video Annotation Dockerfile
# This file need to be inside this repository, to copy all lib dependencies: https://github.com/CarlosPena00/SimpleVideoAnnotation
# Build command: docker build . -t "videoAnnotation:core"
# Run command: docker run -it --rm -e DISPLAY=${DISPLAY} -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix videoannotation:core
# Ubuntu Version: 16.04
# Python 2.7.12
# OpenCV 3.2.0


FROM ubuntu:16.04

#2.7
ENV PYTHON_VERSION 2.7

# Install all dependencies for OpenCV 3.2
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y curl git unzip wget python-pip cmake && \
  apt-get install -y libgtk2.0-dev libtbb2 libtbb-dev && \
  apt-get install -y libpq-dev libgstreamer-plugins-base0.10-0 libcanberra-gtk-module libcanberra-gtk3-module && \
  apt-get -y install python$PYTHON_VERSION-dev wget unzip \
  pkg-config libatlas-base-dev gfortran libavcodec-dev libavformat-dev \
  libswscale-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libv4l-dev \
  && wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && pip install numpy\
  && wget https://github.com/Itseez/opencv/archive/3.2.0.zip -O opencv3.zip \
  && unzip -q opencv3.zip && mv /opencv-3.2.0 /opencv && rm opencv3.zip \
  && wget https://github.com/Itseez/opencv_contrib/archive/3.2.0.zip -O opencv_contrib3.zip \
  && unzip -q opencv_contrib3.zip && mv /opencv_contrib-3.2.0 /opencv_contrib && rm opencv_contrib3.zip \

  # prepare build
  && mkdir /opencv/build && cd /opencv/build \
  && cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D BUILD_PYTHON_SUPPORT=ON \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/opencv_contrib/modules \
    -D BUILD_EXAMPLES=OFF \
    -D WITH_IPP=OFF \
    -D WITH_FFMPEG=ON \
    -D WITH_V4L=ON .. \

  # install
  && cd /opencv/build && make -j$(nproc) && make install && ldconfig \

  #clean
  && apt-get -y remove build-essential cmake git pkg-config libatlas-base-dev gfortran \
  libjasper-dev libgtk2.0-dev libavcodec-dev libavformat-dev \
  libswscale-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libv4l-dev \
  && apt-get clean \
  && rm -rf /opencv /opencv_contrib /var/lib/apt/lists/* && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /root/
RUN mkdir /root/VideoAnnotation
COPY . /root/VideoAnnotation

RUN apt-get update && apt-get install -qqy x11-apps
ENV DISPLAY :0
CMD xeyes

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
CMD ["bash"]