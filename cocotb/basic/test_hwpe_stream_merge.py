#-----------------------------------
# Importing useful tools 
#-----------------------------------
import os
import yaml
import random

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
toplevel     = 'tb_hwpe_stream_merge'
# Specify python test name that contains the @cocotb.test. Usually the name of this test.
module       = "test_hwpe_stream_merge"
# Specify what simulator to use (e.g., verilator, modelsim, icarus)
simulator    = "modelsim"
# Specify build directory
sim_build    = basic_path + "/sim_build/{}/".format(toplevel)
# Get YAML source files path
src_yml_path = hwpe_stream_path + "/src_files.yml"

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

#-----------------------------------
# Add testbench to RTL list
#-----------------------------------
rtl_sources.append('/users/micas/rantonio/no_backup/hwpe-stream-fork/cocotb/basic/tb_hwpe_stream_merge.sv')

for i in range(len(include_folders)):
    include_folders[i] = hwpe_stream_path + '/' + include_folders[i]

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
async def hwpe_stream_merge(dut):

    #-----------------------------------
    # Modifiable parameters
    #-----------------------------------
    CHECK_COUNT   = 10              # Checker parameter
    NB_IN_STREAMS = 2               # DUT parameter
    DATA_WIDTH    = 8               # DUT parameter
    STRB_WIDTH    = DATA_WIDTH / 8  # Don't touch this
    MAX_DATA_VAL  = 2**DATA_WIDTH-1 # Don't touch this
    MAX_STRB_VAL  = 2**STRB_WIDTH-1 # Don't touch this

    # Check first DATA_WIDTH is multiple of 8
    assert ((DATA_WIDTH % 8) == 0), f"{DATA_WIDTH} is not a multiple of 8!"

    #-----------------------------------
    # TB parameters:
    # NB_IN_STREAMS - indicates how many input streams
    # DATA_WIDTH    - indicates literal data width
    # TB drivers ports:
    # logic clk_i
    # logic rst_ni
    # logic clear_i
    # hwpe_stream_intf_stream.sink   push_i [NB_IN_STREAMS-1:0],
    # >> input  valid
    # >> input  data  [DATA_WIDTH-1:0]
    # >> input  strb  [STRB_WIDTH-1:0]
    # >> output ready
    # hwpe_stream_intf_stream.source pop_o
    # >> output valid
    # >> output data  [DATA_WIDTH-1:0]
    # >> output strb  [STRB_WIDTH-1:0]
    # >> input  ready
    #-----------------------------------

    # Initialize clock
    clock = Clock(dut.clk_i, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset or intial values
    dut.rst_ni.value  = 0
    dut.clear_i.value = 0

    # Initialize push_i input values
    for i in range(NB_IN_STREAMS):
        dut.push_i[i].valid.value = 0
        dut.push_i[i].data.value  = 0
        dut.push_i[i].strb.value  = 0
    
    # Initialize pop_o values
    dut.pop_o.ready.value = 0

    # Wait 2 cycles to reset
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)

    # Deassert reset
    dut.rst_ni.value = 1

    #-----------------------------------
    # Testing check
    #-----------------------------------

    cocotb.log.info(f'------------------------------------ START OF TESTING ------------------------------------')

    for i in range(CHECK_COUNT):

        for j in range(NB_IN_STREAMS):

            push_data  = random.randint(0,MAX_DATA_VAL)
            push_valid = random.randint(0,1)
            push_strb  = int(MAX_STRB_VAL)

            pop_ready  = random.randint(0,1)

            dut.push_i[j].data.value  = push_data
            dut.push_i[j].valid.value = push_valid
            dut.push_i[j].strb.value  = push_strb
            dut.pop_o.ready.value     = pop_ready

            cocotb.log.info(f'------------------------------------ INPUT LOG ------------------------------------')
            cocotb.log.info(f'push_i[{j}].data.value  = {hex(push_data)}')
            cocotb.log.info(f'push_i[{j}].valid.value = {    push_valid}')
            cocotb.log.info(f'push_i[{j}].strb.value  = {     push_strb}')
            cocotb.log.info(f'pop_o.ready.value     = {     pop_ready}')
        
        await Timer(1, units="ns")
        
        pop_valid = dut.pop_o.valid.value
        pop_data  = hex(dut.pop_o.data.value)

        cocotb.log.info(f'------------------------------------ OUTPUT LOG ------------------------------------')

        for j in range(NB_IN_STREAMS):
            push_ready = dut.push_i[j].ready.value
            cocotb.log.info(f'push_i[{j}].ready.value = {push_ready}')

        cocotb.log.info(f'pop_o.valid.value      = {pop_valid}')
        cocotb.log.info(f'pop_o.data.value       = { pop_data}')
        





#-----------------------------------
# Pytest run
#-----------------------------------
def test_hwpe_stream_merge():

    global rtl_sources
    global include_folders
    global toplevel
    global module
    global simulator
    global sim_build
    
    run(
        includes        =include_folders,
        verilog_sources =rtl_sources,
        toplevel        =toplevel,   
        module          =module,
        simulator       =simulator,    
        sim_build       =sim_build
    )        


