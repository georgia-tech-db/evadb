# https://www.jenkins.io/doc/book/installing/docker/ - Follow these steps for starting jenkins.
FROM python:3.8

ENV OPENCV_VERSION="4.5.1"

# OpenCV Specific Installation
RUN apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        ffmpeg \
        libsm6 \
        libxext6 \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libopenjp2-7-dev \
        libavformat-dev \
        libpq-dev \
        python3-dev \
        sudo \
        openjdk-11-jdk \
        openjdk-11-jre \
    && pip install numpy \
    && wget -q https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip -O opencv.zip \
    && unzip -qq opencv.zip -d /opt \
    && rm -rf opencv.zip \
    && cmake \
        -D BUILD_TIFF=ON \
        -D BUILD_opencv_java=OFF \
        -D WITH_CUDA=OFF \
        -D WITH_OPENGL=ON \
        -D WITH_OPENCL=ON \
        -D WITH_IPP=ON \
        -D WITH_TBB=ON \
        -D WITH_EIGEN=ON \
        -D WITH_V4L=ON \
        -D BUILD_TESTS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=$(python3.8 -c "import sys; print(sys.prefix)") \
        -D PYTHON_EXECUTABLE=$(which python3.8) \
        -D PYTHON_INCLUDE_DIR=$(python3.8 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
        -D PYTHON_PACKAGES_PATH=$(python3.8 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
        /opt/opencv-${OPENCV_VERSION} \
    && make -j$(nproc) \
    && make install \
    && rm -rf /opt/build/* \
    && rm -rf /opt/opencv-${OPENCV_VERSION}

# Install Java11 (Direct Download) because java-8 is no longer supported
RUN wget https://download.java.net/java/ga/jdk11/openjdk-11_linux-x64_bin.tar.gz && \
    mkdir /opt/jdk-11 && \
    tar -zxf openjdk-11_linux-x64_bin.tar.gz -C /opt/jdk-11

# Add Jenkins user, For Spark Authentication (cannot be done without user)
RUN groupadd --gid 1000 jenkins && \
    useradd --uid 1000 --gid jenkins --shell /bin/bash --home-dir /var/jenkins_home jenkins && \
    mkdir /var/jenkins_home && \
    chown 1000:1000 /var/jenkins_home && \
    echo 'jenkins ALL=NOPASSWD: ALL' >> /etc/sudoers.d/50-jenkins && \
    echo 'Defaults    env_keep += "DEBIAN_FRONTEND"' >> /etc/sudoers.d/env_keep


# Give Permission To Home Directory To Create EVA
RUN mkdir /.eva && chmod -R 777 /.eva
