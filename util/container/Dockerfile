#---------------------
# Ubuntu 22.04 base
#---------------------
FROM ubuntu:22.04

#---------------------
# Install necessary packages
#---------------------
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y install autoconf help2man perl python3 make flex bison g++ 
RUN apt-get -y install libfl2  libfl-dev
RUN apt-get -y install python3 pip

#---------------------
# Compile verilator from source code
#---------------------
RUN git clone https://github.com/verilator/verilator
WORKDIR verilator/
RUN git checkout v5.006
ENV VERILATOR_ROOT=/verilator
RUN autoconf
RUN ./configure
RUN make -j `nproc`
RUN make test
ENV PATH="$VERILATOR_ROOT/bin:$PATH"

#---------------------
# Installing cocotb
#---------------------
WORKDIR tmp/
COPY requirements.txt .
RUN pip install -r requirements.txt

#---------------------
# Importing the hwpe-stream
#---------------------
WORKDIR /
RUN git clone https://github.com/KULeuven-MICAS/hwpe-stream.git
# TODO: fix me later
WORKDIR /hwpe-stream
RUN git checkout add-cocotb-test
RUN git pull
ENV HWPE_STREAM_HOME=/hwpe-stream
RUN echo "SUCCESS! Don't forget to run setup_cocotb.sh!!!"
