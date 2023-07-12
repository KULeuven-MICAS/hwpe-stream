#---------------------------------
# Copyright 2023 KULeuven
# Solderpad Hardware License, Version 0.51, see LICENSE for details.
# SPDX-License-Identifier: SHL-0.51
# Author: Ryan Antonio (ryan.antonio@esat.kuleuven.be)
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
import  cocotb
from    cocotb.triggers       import RisingEdge, Timer
from    cocotb.clock          import Clock
from    cocotb_test.simulator import run

#-----------------------------------
# Importing pytest
#-----------------------------------
import  pytest

#-----------------------------------
# Extracting and setting important variables and paths
#-----------------------------------
hwpe_stream_path = os.getenv("HWPE_STREAM_HOME")
basic_path       = hwpe_stream_path + "/cocotb/basic"

#-----------------------------------
# Top-level definitions 
#-----------------------------------
# Specify top-level module
toplevel     = 'tb_hwpe_stream_split'
# Specify python test name that contains the @cocotb.test. Usually the name of this test.
module       = "test_hwpe_stream_split"
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
CHECK_COUNT   = 5

# DUT parameters
NB_OUT_STREAMS = 2
DATA_WIDTH_IN  = 32

# For random seed logging
RANDOM_SEED = random.randrange(sys.maxsize)
random.seed(RANDOM_SEED)

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
tb_path = hwpe_stream_path + '/cocotb/basic/tb/tb_hwpe_stream_split.sv'
rtl_sources.append(tb_path)

#-----------------------------------
# Verification functions
#-----------------------------------

#-----------------------------------
# Main test bench
#-----------------------------------
# For the main test bench, we need to make sure the ports
# are consistent with the DUT. Double check the main module.
#-----------------------------------
@cocotb.test()
async def hwpe_stream_split(dut):

    #-----------------------------------
    # Local parameters
    # Don't touch these
    #-----------------------------------
    STRB_WIDTH_IN  = int(DATA_WIDTH_IN / 8)  
    MAX_DATA_VAL_I = 2**(DATA_WIDTH_IN)-1      
    MAX_STRB_VAL_I = 2**(STRB_WIDTH_IN)-1
    DATA_WIDTH_OUT = int(DATA_WIDTH_IN/NB_OUT_STREAMS)
    STRB_WIDTH_OUT = int(DATA_WIDTH_OUT/8)

    # Check first DATA_WIDTH_IN is multiple of 8
    assert ((DATA_WIDTH_IN % 8) == 0), f"{DATA_WIDTH_IN} is not a multiple of 8!"

    #-----------------------------------
    # TB parameters:
    # NB_OUT_STREAMS - indicates how many input streams
    # DATA_WIDTH_IN    - indicates literal data width
    # TB drivers ports:
    # logic clk_i
    # logic rst_ni
    # logic clear_i
    # hwpe_stream_intf_stream.sink push_i [NB_OUT_STREAMS-1:0],
    # >> input  valid_i
    # >> input   data_i [DATA_WIDTH_IN-1:0]
    # >> input   strb_i [STRB_WIDTH_IN-1:0]
    # >> output ready_i
    # hwpe_stream_intf_stream.source pop_o
    # >> output valid_o
    # >> output  data_o [DATA_WIDTH_OUT-1:0]
    # >> output  strb_o [STRB_WIDTH_OUT-1:0]
    # >> input  ready_o
    #-----------------------------------

    # Initialize clock
    clock = Clock(dut.clk_i, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset or intial values
    dut.rst_ni.value  = 0
    dut.clear_i.value = 0

    # Initialize push_i input values
    dut.valid_i.value = 0
    dut.data_i.value  = 0
    dut.strb_i.value  = 0
    
    # Initialize pop_o values
    for i in range(NB_OUT_STREAMS):
        dut.ready_o[i].value = 0

    # Wait 2 cycles to reset
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)

    # Deassert reset
    dut.rst_ni.value = 1

    #-----------------------------------
    # Testing check
    #-----------------------------------

    cocotb.log.info(f'------------------------------------ START OF TESTING ------------------------------------')
    cocotb.log.info(f'Running parameters:')
    cocotb.log.info(f'NB_OUT_STREAMS:{NB_OUT_STREAMS}')
    cocotb.log.info(f'DATA_WIDTH_IN :{DATA_WIDTH_IN}')
    cocotb.log.info(f'RANDOM_SEED   :{RANDOM_SEED}')
    cocotb.log.info(f'------------------------------------------------------------------------------------------')

    for i in range(CHECK_COUNT):

        cocotb.log.info(f'------------------------------------ ITERATION # {i} ------------------------------------')

        #-----------------------------------
        # Inputting stimuli
        #-----------------------------------

        # Initialize empty arrays
        pop_data  = [0]*NB_OUT_STREAMS
        pop_valid = [0]*NB_OUT_STREAMS
        pop_strb  = [0]*NB_OUT_STREAMS
        pop_ready = [0]*NB_OUT_STREAMS

        # Set stimuli values to drive DUT
        push_data  = random.randint(0,MAX_DATA_VAL_I)
        push_valid = random.randint(0,1)
        push_strb  = random.randint(0,MAX_STRB_VAL_I)
        
        # Load stimuli values to push in
        dut. data_i.value = push_data
        dut.valid_i.value = push_valid
        dut. strb_i.value = push_strb

        for j in range(NB_OUT_STREAMS):
            pop_ready[j]         = random.randint(0,1)
            dut.ready_o[j].value = pop_ready[j]

        # Propagate data
        await Timer(1, units="ns")

        #-----------------------------------
        # Extracting outputs
        #-----------------------------------
        for j in range(NB_OUT_STREAMS):

            pop_data [j] = dut. data_o[j].value
            pop_valid[j] = dut.valid_o[j].value 
            pop_strb [j] = dut. strb_o[j].value 
            pop_ready[j] = dut.ready_o[j].value

        # Push ready direction is an output to the input side
        push_ready = dut.ready_i.value


        #-----------------------------------
        # Logging data
        #-----------------------------------
        cocotb.log.info(f'===== INPUT LOG =====')

        cocotb.log.info(f'----- INPUT STREAM -----')
        cocotb.log.info(f'push_i.data.value  = { hex(push_data)}')
        cocotb.log.info(f'push_i.valid.value = {     push_valid}')
        cocotb.log.info(f'push_i.strb.value  = { bin(push_strb)}')
        cocotb.log.info(f'push_i.ready.value = {bin(push_ready)}')

        cocotb.log.info(f'===== OUTPUT LOG =====')

        for j in range(NB_OUT_STREAMS):

            cocotb.log.info(f'----- OUTPUT STREAM # {j} -----')
            cocotb.log.info(f'pop_o{NB_OUT_STREAMS-j}.data.value  = { hex(pop_data[j])}')
            cocotb.log.info(f'pop_o{NB_OUT_STREAMS-j}.valid.value = {     pop_valid[j]}')
            cocotb.log.info(f'pop_o{NB_OUT_STREAMS-j}.strb.value  = { bin(pop_strb[j])}')
            cocotb.log.info(f'pop_o{NB_OUT_STREAMS-j}.ready.value = {bin(pop_ready[j])}')

        #-----------------------------------
        # Assertion checks
        #-----------------------------------

        # Checking for output mismatch
        # Expected output should be a simple concatenation of inputs
        # Note that MSB is higher number in array
        data_check  = 0
        strb_check  = 0
        valid_check = 0
        ready_check = 0

        for j in range(NB_OUT_STREAMS-1,-1,-1):

            data_check   = (data_check << DATA_WIDTH_OUT) + pop_data[j]
            strb_check   = (strb_check << STRB_WIDTH_OUT) + pop_strb[j]
            valid_check += pop_valid[j]
            ready_check += pop_ready[j]

        # Check if data is correct
        assert(data_check == push_data), f"ERROR! Output mismatch - Expected output: {hex(data_check)}; Actual output: {hex(push_data)}"

        # Check if valid is correct
        valid_expect = math.floor(valid_check/NB_OUT_STREAMS)
        assert(valid_expect == push_valid), f"ERROR! Valid mismatch - Expected valid: {valid_expect}; Actual output: {push_valid}"

        # Check if strb is correct
        assert(strb_check == push_strb), f"ERROR! Output mismatch - Expected output: {bin(strb_check)}; Actual output: {bin(push_strb)}"

        # Check if ready is correct
        ready_check = math.floor(ready_check/NB_OUT_STREAMS)
        assert (push_ready == ready_check), f"ERROR! Ready mismatch - Double check ready values. Output ready input should be the same for input ready signals."

#-----------------------------------
# Pytest run
#-----------------------------------

# Parametrization
@pytest.mark.parametrize(
"parameters", [
    {"DATA_WIDTH_IN": str(DATA_WIDTH_IN), "NB_OUT_STREAMS": str(NB_OUT_STREAMS)}
])

# Main test run
def test_hwpe_stream_split(parameters):

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