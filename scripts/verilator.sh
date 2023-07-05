#!/bin/bash

#-------------------------------------
# Installing verilator for cocotb
#-------------------------------------

# REQUIRED verilator version
export VL_VERSION=v4.106

# Path where the Verilator git will be cloned
export VL_INSTALL_PATH=$HOME/verilator

# Setting Verilator root with appropriate version
export VERILATOR_ROOT=$VL_INSTALL_PATH/verilator-$VL_VERSION

# Creating install directory
mkdir -p $VL_INSTALL_PATH && cd $VL_INSTALL_PATH 

# Clone the main Verilator repo
git clone https://github.com/verilator/verilator

# Moving
mv $VL_INSTALL_PATH/verilator verilator-$VL_VERSION && cd $VL_INSTALL_PATH/verilator-$VL_VERSION # Move Verilator
cd $VL_INSTALL_PATH/verilator-$VL_VERSION

# Making sure to checkout the REQUIRED version
git checkout $VL_VERSION

# Compile and test verilator
autoconf && ./configure && make -j16 && make test