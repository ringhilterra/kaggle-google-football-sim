ARG DOCKER_BASE
FROM $DOCKER_BASE
ARG DEVICE

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get --no-install-recommends install -yq git cmake build-essential \
  libgl1-mesa-dev libsdl2-dev \
  libsdl2-image-dev libsdl2-ttf-dev libsdl2-gfx-dev libboost-all-dev \
  libdirectfb-dev libst-dev mesa-utils xvfb x11vnc \
  libsdl-sge-dev python3-pip

RUN apt install ffmpeg
RUN apt install screen

RUN python3 -m pip install --upgrade pip setuptools
RUN pip3 install --use-feature=2020-resolver --no-cache-dir tensorflow==1.15.* dm-sonnet==1.* psutil

RUN pip3 install --use-feature=2020-resolver --no-cache-dir git+https://github.com/openai/baselines.git@master


RUN pip3 install --use-feature=2020-resolver --no-cache-dir git+https://github.com/openai/baselines.git@master

COPY . /gfootball
RUN cd /gfootball && pip3 install --use-feature=2020-resolver .

RUN git clone -q https://github.com/Kaggle/kaggle-environments.git
RUN cd kaggle-environments && pip install -q .
RUN pip3 install requests
RUN pip3 install jupyterlab
RUN pip3 install matplotlib
RUN pip3 install ffmpeg
RUN pip3 install pandas
RUN pip3 install sklearn
RUN pip3 install lightgbm
RUN cd ..

WORKDIR '/fmountgf'
