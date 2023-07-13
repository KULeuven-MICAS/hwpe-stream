#---------------------------------
# Copyright 2023 KULeuven
# Solderpad Hardware License, Version 0.51, see LICENSE for details.
# SPDX-License-Identifier: SHL-0.51
# Author: Ryan Antonio (ryan.antonio@esat.kuleuven.be)
#---------------------------------
# Test Description:
# - test_hwpe_stream_fence.py tests the synchronization
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
toplevel     = 'tb_hwpe_stream_fence'
# Specify python test name that contains the @cocotb.test. Usually the name of this test.
module       = "test_hwpe_stream_fence"
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
CLK_COUNT  = 5

# DUT parameters
NB_STREAMS = 2
DATA_WIDTH = 16

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
tb_path = hwpe_stream_path + '/cocotb/basic/tb/tb_hwpe_stream_fence.sv'
rtl_sources.append(tb_path)

#-----------------------------------
# Fence model
#-----------------------------------
class stimMon():

    def __init__(self):

        self.data       = 0
        self.strb       = 0
        self.valid      = 0

        self.hold_data  = 0
        self.hold_strb  = 0
        self.hold_state = 0

    def drive_input(self, dut_ready_i, dut_ready_all_o):

        self.data  = random.randint(0,MAX_DATA_VAL)
        self.strb  = random.randint(0,MAX_STRB_VAL)

        if(self.valid == 0):
            self.valid = random.randint(0,1)

        if(dut_ready_i):
            self.valid = 0

        if(self.valid & (self.hold_state == 0)):
            self.hold_data = self.data
            self.hold_strb = self.strb

        if(self.valid):
            self.hold_state = 1

        if(self.hold_state):
            return self.hold_data, self.hold_strb
        else:
            return self.data, self.strb

        


            
#-----------------------------------
# Main test bench
#-----------------------------------
# For the main test bench, we need to make sure the ports
# are consistent with the DUT. Double check the main module.
#-----------------------------------
@cocotb.test()
async def hwpe_stream_fence(dut):

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
    for i in range(NB_STREAMS):
        dut.valid_i[i].value = 0
        dut.data_i [i].value = 0
        dut.strb_i [i].value = 0
        dut.ready_o[i].value = 0

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
    cocotb.log.info(f'NB_STREAMS :{NB_STREAMS}')
    cocotb.log.info(f'DATA_WIDTH :{DATA_WIDTH}')
    cocotb.log.info(f'RANDOM_SEED:{RANDOM_SEED}')
    cocotb.log.info(f'------------------------------------------------------------------------------------------')

    # Initialize empty arrays for stimuli
    push_data  = [0]*NB_STREAMS
    push_valid = [0]*NB_STREAMS
    push_strb  = [0]*NB_STREAMS
    push_ready = [0]*NB_STREAMS

    pop_data   = [0]*NB_STREAMS
    pop_valid  = [0]*NB_STREAMS
    pop_strb   = [0]*NB_STREAMS
    pop_ready  = [0]*NB_STREAMS

    hold_data  = [0]*NB_STREAMS
    hold_strb  = [0]*NB_STREAMS


    for i in range(CLK_COUNT):

        cocotb.log.info(f'------------------------------------ CYCLE # {i} ------------------------------------')

        #-----------------------------------
        # Inputting stimuli
        #-----------------------------------
        if(all((elem == 1) for elem in pop_ready)):
            for j in range(NB_STREAMS):
                push_valid[j] = 0
                pop_ready[j] = 0

        for j in range(NB_STREAMS):

            if(push_valid[j]==0):
                push_data [j] = random.randint(0,MAX_DATA_VAL)
                push_valid[j] = random.randint(0,1)
                push_strb [j] = random.randint(0,MAX_STRB_VAL)
            else:
                pass

            if(pop_ready[j]==0):
                pop_ready[j] = random.randint(0,1)
        
            # Load stimuli values to push in
            dut. data_i[j].value = push_data [j]
            dut.valid_i[j].value = push_valid[j]
            dut. strb_i[j].value = push_strb [j]
            dut.ready_o[j].value = pop_ready [j]

        # Propagate data
        await Timer(1, units="ns")

        #-----------------------------------
        # Extracting outputs
        #-----------------------------------
        for j in range(NB_STREAMS):

            pop_data [j]  = dut. data_o[j].value
            pop_valid[j]  = dut.valid_o[j].value 
            pop_strb [j]  = dut. strb_o[j].value 
            push_ready[j] = dut.ready_i[j].value

        #-----------------------------------
        # Logging data
        #-----------------------------------
        cocotb.log.info(f'===== INPUT LOG =====')

        for j in range(NB_STREAMS):

            cocotb.log.info(f'----- INPUT STREAM #{j} -----')
            cocotb.log.info(f'push_i{NB_STREAMS-j}.data.value  = { hex(push_data[j])}')
            cocotb.log.info(f'push_i{NB_STREAMS-j}.valid.value = {     push_valid[j]}')
            cocotb.log.info(f'push_i{NB_STREAMS-j}.strb.value  = { bin(push_strb[j])}')
            cocotb.log.info(f'push_i{NB_STREAMS-j}.ready.value = {bin(push_ready[j])}')

        cocotb.log.info(f'===== OUTPUT LOG =====')

        for j in range(NB_STREAMS):

            cocotb.log.info(f'----- OUTPUT STREAM # {j} -----')
            cocotb.log.info(f'pop_o{NB_STREAMS-j}.data.value  = { hex(pop_data[j])}')
            cocotb.log.info(f'pop_o{NB_STREAMS-j}.valid.value = {     pop_valid[j]}')
            cocotb.log.info(f'pop_o{NB_STREAMS-j}.strb.value  = { bin(pop_strb[j])}')
            cocotb.log.info(f'pop_o{NB_STREAMS-j}.ready.value = {bin(pop_ready[j])}')

        #-----------------------------------
        # Assertion checks
        #-----------------------------------


        # TODO: TEST IS INCOMPLETE, COMPLETE NEXT TIME!

        '''
        # Checking for output mismatch
        # Expected output should be a simple concatenation of inputs
        # Note that MSB is higher number in array
        data_check  = 0
        strb_check  = 0
        valid_check = 0
        ready_check = 0

        for j in range(NB_STREAMS-1,-1,-1):

            data_check   = (data_check << DATA_WIDTH) + pop_data[j]
            strb_check   = (strb_check << STRB_WIDTH) + pop_strb[j]
            valid_check += pop_valid[j]
            ready_check += pop_ready[j]

        # Check if data is correct
        assert(data_check == push_data), f"ERROR! Output mismatch - Expected output: {hex(data_check)}; Actual output: {hex(push_data)}"

        # Check if valid is correct
        valid_expect = math.floor(valid_check/NB_STREAMS)
        assert(valid_expect == push_valid), f"ERROR! Valid mismatch - Expected valid: {valid_expect}; Actual output: {push_valid}"

        # Check if strb is correct
        assert(strb_check == push_strb), f"ERROR! Output mismatch - Expected output: {bin(strb_check)}; Actual output: {bin(push_strb)}"

        # Check if ready is correct
        ready_check = math.floor(ready_check/NB_STREAMS)
        assert (push_ready == ready_check), f"ERROR! Ready mismatch - Double check ready values. Output ready input should be the same for input ready signals."
        '''

#-----------------------------------
# Pytest run
#-----------------------------------

# Parametrization
@pytest.mark.parametrize(
"parameters", [
    {"DATA_WIDTH": str(DATA_WIDTH), "NB_STREAMS": str(NB_STREAMS)}
])

# Main test run
def test_hwpe_stream_fence(parameters):

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