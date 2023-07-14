#---------------------------------
# Copyright 2023 KULeuven
# Solderpad Hardware License, Version 0.51, see LICENSE for details.
# SPDX-License-Identifier: SHL-0.51
# Author: Ryan Antonio (ryan.antonio@esat.kuleuven.be)
#---------------------------------
# Test Description:
# - test_hwpe_stream_demux_static.py tests the synchronization
#   between the input and output mapping of streams.
# - the synchronization is handled by the valid-ready signals
# - best way to test this is to model a random buffer from input
#   then test if the output gets the sequenced data correctly
#---------------------------------

#-----------------------------------
# Importing useful tools 
#-----------------------------------
import os
import yaml
import random
import math
import sys

#-----------------------------------
# Importing cocotb 
#-----------------------------------
import cocotb
from   cocotb.triggers       import RisingEdge, Timer
from   cocotb.clock          import Clock
from   cocotb_test.simulator import run

#-----------------------------------
# Importing pytest
#-----------------------------------
import pytest

#-----------------------------------
# Extracting and setting important variables and paths
#-----------------------------------
hwpe_stream_path = os.getenv("HWPE_STREAM_HOME")
basic_path       = hwpe_stream_path + "/cocotb/basic"

#-----------------------------------
# Top-level definitions 
#-----------------------------------
# Specify top-level module
toplevel     = 'tb_hwpe_stream_demux_static'
# Specify python test name that contains the @cocotb.test. Usually the name of this test.
module       = "test_hwpe_stream_demux_static"
# Specify what simulator to use (e.g., verilator, modelsim, icarus)
simulator    = "verilator"
# Specify build directory
sim_build    = basic_path + "/test/sim_build/{}/".format(toplevel)
# Get YAML source files path
src_yml_path = hwpe_stream_path + "/src_files.yml"

#-----------------------------------
# Global parameters for testing
# TODO: These are modifiable so change whenever needed
#-----------------------------------
# Checker parameter
CHECK_COUNT  = 5

# DUT parameters
DATA_WIDTH     = 32 # Note main module does not have parameter
NB_OUT_STREAMS = 2

# For random seed logging
RANDOM_SEED = random.randrange(sys.maxsize)
random.seed(RANDOM_SEED)

#-----------------------------------
# Local parameters
# Don't touch these
#-----------------------------------
SEL_WIDTH    = int(math.log(NB_OUT_STREAMS,2))
STRB_WIDTH   = int(DATA_WIDTH / 8)  
MAX_DATA_VAL = 2**(DATA_WIDTH)-1      
MAX_STRB_VAL = 2**(STRB_WIDTH)-1
MAX_SEL_VAL  = 2**(SEL_WIDTH)-1

#-----------------------------------
# Get YAML source
#-----------------------------------
with open(src_yml_path,"r") as src_files:
    try:
        yaml_dict = yaml.safe_load(src_files)
    except yaml.YAMLError as exc:
        print(exc)

#-----------------------------------
# Extract source from YAML
# Also append the main working path
#-----------------------------------
include_folders = yaml_dict['hwpe-stream']['incdirs']
rtl_sources     = yaml_dict['hwpe-stream']['files']

for i in range(len(rtl_sources)):
    rtl_sources[i] = hwpe_stream_path + '/' + rtl_sources[i]

for i in range(len(include_folders)):
    include_folders[i] = hwpe_stream_path + '/' + include_folders[i]

#-----------------------------------
# Add testbench to RTL list
#-----------------------------------
tb_path = hwpe_stream_path + '/cocotb/basic/tb/tb_hwpe_stream_demux_static.sv'
rtl_sources.append(tb_path)
            
#-----------------------------------
# Main test bench
#-----------------------------------
# For the main test bench, we need to make sure the ports
# are consistent with the DUT. Double check the main module.
#-----------------------------------
@cocotb.test()
async def hwpe_stream_demux_static(dut):

    # Check first DATA_WIDTH is multiple of 8
    assert ((DATA_WIDTH % 8) == 0), f"{DATA_WIDTH} is not a multiple of 8!"

    #-----------------------------------
    # TB parameters:
    # NB_STREAMS - indicates how many input streams
    # DATA_WIDTH    - indicates literal data width
    # TB drivers ports:
    # logic clk_i
    # logic rst_ni
    # logic clear_i
    # hwpe_stream_intf_stream.sink push_i [NB_STREAMS-1:0],
    # >> input  valid_i
    # >> input   data_i [DATA_WIDTH-1:0]
    # >> input   strb_i [STRB_WIDTH-1:0]
    # >> output ready_i
    # hwpe_stream_intf_stream.source pop_o
    # >> output valid_o
    # >> output  data_o [DATA_WIDTH-1:0]
    # >> output  strb_o [STRB_WIDTH-1:0]
    # >> input  ready_o
    #-----------------------------------

    # Initialize clock
    clock = Clock(dut.clk_i, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset or intial values
    dut.rst_ni.value  = 0
    dut.clear_i.value = 0

    # Initialize all inputs
    dut.push_valid_i.value = 0
    dut.push_ready_i.value = 0
    dut.push_data_i .value = 0
    dut.push_strb_i .value = 0

    for i in range(NB_OUT_STREAMS):
        dut.pop_ready_o[i].value = 0

    dut.sel_i.value = 0

    # Wait 2 cycles to reset
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)

    # Deassert reset
    dut.rst_ni.value = 1

    # Allow time to propagate
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)

    #-----------------------------------
    # Testing check
    #-----------------------------------

    cocotb.log.info(f'------------------------------------ START OF TESTING ------------------------------------')
    cocotb.log.info(f'Running parameters:')
    cocotb.log.info(f'NB_OUT_STREAMS:{NB_OUT_STREAMS}')
    cocotb.log.info(f'RANDOM_SEED   :{RANDOM_SEED}')
    cocotb.log.info(f'------------------------------------------------------------------------------------------')

    for i in range(CHECK_COUNT):

        cocotb.log.info(f'------------------------------------ TEST ITERATION # {i} ------------------------------------')

        #-----------------------------------
        # Inputting stimuli
        #-----------------------------------
        pop_ready_o = [0]*NB_OUT_STREAMS
        pop_data_o  = [0]*NB_OUT_STREAMS
        pop_valid_o = [0]*NB_OUT_STREAMS
        pop_strb_o  = [0]*NB_OUT_STREAMS

        #-----------------------------------
        # Inputting stimuli
        #-----------------------------------

        push_valid_i = random.randint(0,1)
        push_data_i  = random.randint(0,MAX_DATA_VAL)
        push_strb_i  = random.randint(0,MAX_STRB_VAL)
        sel_i        = random.randint(0,MAX_SEL_VAL)

        for j in range(NB_OUT_STREAMS):
            pop_ready_o[j]    = random.randint(0,1)

        dut.push_valid_i.value = push_valid_i
        dut. push_data_i.value = push_data_i
        dut. push_strb_i.value = push_strb_i
        dut.       sel_i.value = sel_i

        for j in range(NB_OUT_STREAMS):
            dut.pop_ready_o[j].value = pop_ready_o[j]

        # Propagate data
        await Timer(1, units="ns")

        #-----------------------------------
        # Extracting outputs
        #-----------------------------------
        for j in range(NB_OUT_STREAMS):
            pop_data_o [j] = int(dut. pop_data_o[j].value)
            pop_valid_o[j] = int(dut.pop_valid_o[j].value)
            pop_strb_o [j] = int(dut. pop_strb_o[j].value)

        push_ready_i = int(dut.push_ready_i.value)

        #-----------------------------------
        # Logging data
        #-----------------------------------
        cocotb.log.info(f'===== INPUT LOG =====')

        cocotb.log.info(f'----- INPUT STREAM -----')
        cocotb.log.info(f'push_data_i  = { hex(push_data_i)}')
        cocotb.log.info(f'push_valid_i = {     push_valid_i}')
        cocotb.log.info(f'push_strb_i  = { bin(push_strb_i)}')
        cocotb.log.info(f'push_ready_i = {bin(push_ready_i)}')

        cocotb.log.info(f'----- SELECT SIGNAL -----')
        cocotb.log.info(f'sel_i = {bin(sel_i)}')

        cocotb.log.info(f'===== OUTPUT LOG =====')

        for j in range(NB_OUT_STREAMS):

            cocotb.log.info(f'----- OUTPUT STREAM #{j} -----')
            cocotb.log.info(f'pop_data_o [{j}] = { hex(pop_data_o[j])}')
            cocotb.log.info(f'pop_valid_o[{j}] = {    pop_valid_o[j] }')
            cocotb.log.info(f'pop_strb_o [{j}] = { bin(pop_strb_o[j])}')
            cocotb.log.info(f'pop_ready_o[{j}] = {bin(pop_ready_o[j])}')

        #-----------------------------------
        # Assertion checks
        #-----------------------------------

        for j in range(NB_OUT_STREAMS):
            # Check if data is correct
            assert(push_data_i  == pop_data_o[j]),  f"ERROR! STREAM #{j}  data mismatch - Expected output: {hex(push_data_i)}; Actual output: {hex(pop_data_o[j])}"
            
            # Check if strb is correct
            assert(push_strb_i  == pop_strb_o[j]),  f"ERROR! STREAM #{j}  strb mismatch - Expected output: {hex(push_strb_i)}; Actual output: {hex(pop_strb_o[j])}"

            # Check if valid is correct
            if(j == sel_i):
                assert(push_valid_i == pop_valid_o[j]), f"ERROR! STREAM #{j} valid mismatch - Expected output: {hex(push_valid_i)}; Actual output: {hex(pop_valid_o[j])}"
            else:
               assert(0 == pop_valid_o[j]), f"ERROR! STREAM #{j} valid mismatch - Expected output: {hex(0)}; Actual output: {hex(pop_valid_o[j])}"
 
            # Check if ready is correct
            if(j == sel_i):
                assert(push_ready_i == pop_ready_o[j]), f"ERROR! STREAM #{j} ready mismatch - Expected output: {hex(pop_ready_o[j])}; Actual output: {hex(push_ready_i)}"

#-----------------------------------
# Pytest run
#-----------------------------------

# Parametrization
@pytest.mark.parametrize(
"parameters", [
    {"NB_OUT_STREAMS": str(NB_OUT_STREAMS)}
])

# Main test run
def test_hwpe_stream_demux_static(parameters):

    global rtl_sources
    global include_folders
    global toplevel
    global module
    global simulator
    global sim_build
    
    run(
        includes        = include_folders,
        verilog_sources = rtl_sources,
        toplevel        = toplevel,   
        module          = module,
        simulator       = simulator,    
        sim_build       = sim_build,
        parameters      = parameters
    )