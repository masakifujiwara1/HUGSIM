FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

SHELL ["/bin/bash", "-c"]

ARG USER_ID=1000
ARG USER_GID=${USER_ID}
ARG USER_NAME=ubuntu
ARG PASSWORD=ubuntu

RUN if id -u ${USER_ID}; then userdel "$(id -un ${USER_ID})"; fi

RUN groupadd --gid ${USER_GID} ${USER_NAME} && \
    useradd --uid ${USER_ID} --gid ${USER_GID} -m ${USER_NAME} && \
    apt-get update && \
    apt-get install -y sudo && \
    echo "${USER_NAME}:${PASSWORD}" | chpasswd && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /home/${USER_NAME}
ENV TERM=xterm-256color

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

RUN echo "Asia/Tokyo" > /etc/timezone && \
    ln -snf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    apt-get update && \
    apt-get install -q -y --no-install-recommends tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN apt-get update && \
    apt-get install -q -y --no-install-recommends locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential \
        can-utils \
        command-not-found \
        curl \
        gedit \
        git \
        gnupg2 \
        less \
        lsb-release \
        mesa-utils \
        nautilus \
        net-tools \
        tmux \
        vim \
        wget \
        x11-apps \
        xdg-utils \
        xsel && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libbz2-dev \
        libdb-dev \
        libffi-dev \
        libgdbm-dev \
        liblzma-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        uuid-dev \
        zlib1g-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get autoremove -y

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

RUN git clone https://github.com/masakifujiwara1/tmux_config.git && \
    cp tmux_config/.tmux.conf ~/ && \
    rm -rf tmux_config

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

CMD ["bash"]
