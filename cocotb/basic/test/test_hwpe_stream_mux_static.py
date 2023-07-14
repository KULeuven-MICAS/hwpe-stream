#---------------------------------
# Copyright 2023 KULeuven
# Solderpad Hardware License, Version 0.51, see LICENSE for details.
# SPDX-License-Identifier: SHL-0.51
# Author: Ryan Antonio (ryan.antonio@esat.kuleuven.be)
#---------------------------------
# Test Description:
# - test_hwpe_stream_mux_static.py tests the synchronization
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
toplevel     = 'tb_hwpe_stream_mux_static'
# Specify python test name that contains the @cocotb.test. Usually the name of this test.
module       = "test_hwpe_stream_mux_static"
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
DATA_WIDTH = 32 # Note main module does not have parameter

# For random seed logging
RANDOM_SEED = random.randrange(sys.maxsize)
random.seed(RANDOM_SEED)

#-----------------------------------
# Local parameters
# Don't touch these
#-----------------------------------
STRB_WIDTH   = int(DATA_WIDTH / 8)  
MAX_DATA_VAL = 2**(DATA_WIDTH)-1      
MAX_STRB_VAL = 2**(STRB_WIDTH)-1

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
tb_path = hwpe_stream_path + '/cocotb/basic/tb/tb_hwpe_stream_mux_static.sv'
rtl_sources.append(tb_path)
            
#-----------------------------------
# Main test bench
#-----------------------------------
# For the main test bench, we need to make sure the ports
# are consistent with the DUT. Double check the main module.
#-----------------------------------
@cocotb.test()
async def hwpe_stream_mux_static(dut):

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
    dut.push_0_valid_i.value = 0
    dut.push_0_ready_i.value = 0
    dut.push_0_data_i .value = 0
    dut.push_0_strb_i .value = 0

    dut.push_1_valid_i.value = 0
    dut.push_1_ready_i.value = 0
    dut.push_1_data_i .value = 0
    dut.push_1_strb_i .value = 0

    dut.pop_ready_o.value = 0

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
    cocotb.log.info(f'DATA_WIDTH :{DATA_WIDTH}')
    cocotb.log.info(f'RANDOM_SEED:{RANDOM_SEED}')
    cocotb.log.info(f'------------------------------------------------------------------------------------------')

    for i in range(CHECK_COUNT):

        cocotb.log.info(f'------------------------------------ TEST ITERATION # {i} ------------------------------------')

        #-----------------------------------
        # Inputting stimuli
        #-----------------------------------

        push_0_valid_i = random.randint(0,1)
        push_0_data_i  = random.randint(0,MAX_DATA_VAL)
        push_0_strb_i  = random.randint(0,MAX_STRB_VAL)

        push_1_valid_i = random.randint(0,1)
        push_1_data_i  = random.randint(0,MAX_DATA_VAL)
        push_1_strb_i  = random.randint(0,MAX_STRB_VAL)

        pop_ready_o    = random.randint(0,1)
        sel_i          = random.randint(0,1)

        dut.push_0_valid_i.value = push_0_valid_i
        dut.push_0_data_i .value = push_0_data_i
        dut.push_0_strb_i .value = push_0_strb_i

        dut.push_1_valid_i.value = push_1_valid_i
        dut.push_1_data_i .value = push_1_data_i
        dut.push_1_strb_i .value = push_1_strb_i

        dut.pop_ready_o.value    = pop_ready_o
        dut.sel_i.value          = sel_i

        # Propagate data
        await Timer(1, units="ns")

        #-----------------------------------
        # Extracting outputs
        #-----------------------------------
        pop_data_o     = int(dut. pop_data_o.value)
        pop_valid_o    = int(dut.pop_valid_o.value)
        pop_strb_o     = int(dut. pop_strb_o.value)
        push_0_ready_i = int(dut.push_0_ready_i.value)
        push_1_ready_i = int(dut.push_1_ready_i.value)

        #-----------------------------------
        # Logging data
        #-----------------------------------
        cocotb.log.info(f'===== INPUT LOG =====')

        cocotb.log.info(f'----- INPUT STREAM 0 -----')
        cocotb.log.info(f'push_0_data_i  = { hex(push_0_data_i)}')
        cocotb.log.info(f'push_0_valid_i = {     push_0_valid_i}')
        cocotb.log.info(f'push_0_strb_i  = { bin(push_0_strb_i)}')
        cocotb.log.info(f'push_0_ready_i = {bin(push_0_ready_i)}')

        cocotb.log.info(f'----- INPUT STREAM 1 -----')
        cocotb.log.info(f'push_1_data_i  = { hex(push_1_data_i)}')
        cocotb.log.info(f'push_1_valid_i = {     push_1_valid_i}')
        cocotb.log.info(f'push_1_strb_i  = { bin(push_1_strb_i)}')
        cocotb.log.info(f'push_1_ready_i = {bin(push_1_ready_i)}')

        cocotb.log.info(f'----- SELECT SIGNAL -----')
        cocotb.log.info(f'sel_i = {bin(sel_i)}')


        cocotb.log.info(f'===== OUTPUT LOG =====')

        

        cocotb.log.info(f'----- OUTPUT STREAM # -----')
        cocotb.log.info(f'pop_data_o  = { hex(pop_data_o)}')
        cocotb.log.info(f'pop_valid_o = {     pop_valid_o}')
        cocotb.log.info(f'pop_strb_o  = { bin(pop_strb_o)}')
        cocotb.log.info(f'pop_ready_o = {bin(pop_ready_o)}')

        #-----------------------------------
        # Assertion checks
        #-----------------------------------

        # Checking is simple, depending on the state of sel_i, we check if the output matches
        if(sel_i == 1):
            expected_data    = push_1_data_i
            expected_strb    = push_1_strb_i
            expected_valid   = push_1_valid_i
            expected_ready_1 = push_1_ready_i
            expected_ready_0 = 0
        else:
            expected_data    = push_0_data_i
            expected_strb    = push_0_strb_i
            expected_valid   = push_0_valid_i
            expected_ready_1 = 0
            expected_ready_0 = push_0_ready_i
        

        # Check if data is correct
        assert(expected_data== pop_data_o), f"ERROR! data mismatch - Expected output: {hex(expected_data)}; Actual output: {hex(pop_data_o)}"
        
        # Check if strb is correct
        assert(expected_strb== pop_strb_o), f"ERROR! strb mismatch - Expected output: {hex(expected_strb)}; Actual output: {hex(pop_strb_o)}"

        # Check if valid is correct
        assert(expected_valid== pop_valid_o), f"ERROR! valid mismatch - Expected output: {hex(expected_valid)}; Actual output: {hex(pop_valid_o)}"

        # Check if ready are correct
        assert(expected_ready_0== push_0_ready_i), f"ERROR! ready_0 mismatch - Expected output: {hex(expected_ready_0)}; Actual output: {hex(push_0_ready_i)}"
        assert(expected_ready_1== push_1_ready_i), f"ERROR! ready_1 mismatch - Expected output: {hex(expected_ready_1)}; Actual output: {hex(push_1_ready_i)}"


#-----------------------------------
# Pytest run
#-----------------------------------

# Parametrization
@pytest.mark.parametrize(
"parameters", [
    {"DATA_WIDTH": str(DATA_WIDTH)}
])

# Main test run
def test_hwpe_stream_mux_static(parameters):

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