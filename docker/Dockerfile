FROM jetbot/jetbot:jupyter-0.4.3-32.5.0

# ==============
# INSTALL JETSON INFERENCE
# ==============

RUN apt-get update && \
    apt-get install git cmake libpython3-dev python3-numpy && \
    git clone --recursive https://github.com/dusty-nv/jetson-inference && \
    cd jetson-inference && \
    sed -i 's/nvcaffe_parser/nvparsers/g' CMakeLists.txt && \
    mkdir build && \
    cd build && \
    cmake ../ && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    pip3 install websockets
