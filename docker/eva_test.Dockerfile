FROM python:3.8

ENV OPENCV_VERSION="4.5.1"

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

# install system-wide package
# RUN apt-get -y install software-properties-common \
#     && add-apt-repository -u ppa:openjdk-r/ppa \
#     && apt-get --allow-unauthenticated -y install openjdk-8-jdk openjdk-8-jre \
#     && rm -rf /var/lib/apt/lists/* \
#     && apt-get -qq autoremove \
#     && apt-get -qq clean

# Install OpenJDK-8
# RUN apt-get -y install software-properties-common && \
#     apt-get --allow-releaseinfo-change update && \
#     add-apt-repository ppa:webupd8team/java && \
#     apt-get update && \
#     apt-get install -y oracle-java8-installer && \
#     apt-get install -y ant

# RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee /etc/apt/sources.list.d/webupd8team-java.list && \
#     echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list && \
#     echo oracle-java8-installer shared/accepted-oracle-licence-v1-1 boolean true | /usr/bin/debconf-set-selections && \
#     apt-get --allow-unauthenticated update && \
#     apt-get --allow-unauthenticated update install oracle-java8-installer

# Fix certificate issues
# RUN apt-get install ca-certificates-java && \
#     apt-get clean && \
#     update-ca-certificates -f;

# Install OpenJDK-8
RUN apt-get -y install software-properties-common \
    && apt-get --allow-releaseinfo-change update \
    && add-apt-repository ppa:webupd8team/java \
    && apt-get update \
    && apt-get install openjdk-10-jdk

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-10-openjdk-amd64/
RUN export JAVA_HOME

# Give Permission To Home Directory
RUN mkdir /.eva && chmod -R 777 /.eva
