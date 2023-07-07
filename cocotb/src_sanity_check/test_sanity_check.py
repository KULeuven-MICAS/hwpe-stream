#-----------------------------------
# Importing cocotb 
#-----------------------------------

import  cocotb
from    cocotb.triggers       import RisingEdge
from    cocotb.clock          import Clock
from    cocotb_test.simulator import run

#-----------------------------------
# Importing pytest
#-----------------------------------
import  pytest

#-----------------------------------
# Main test bench
#-----------------------------------
@cocotb.test()
async def sanity_check(dut):

    # Initialize clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1

    # Wait 2 cycles to reset
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Deassert reset
    dut.reset.value = 0

    # Clock 10 more times and check counter value
    for i in range(10):
        await RisingEdge(dut.clk)
        count_out = int(dut.count.value)
        cocotb.log.info(f'Counter:{count_out}')


#-----------------------------------
# Pytest run
#-----------------------------------
def test_sanity_check():

    # Specify include sources
    include_folders = ['']
    # Specify main rtl_sources
    rtl_sources     = ['/src_sanity_check/sanity_counter.sv']
    # Specify top-level module
    toplevel        = 'sanity_counter'
    # Specify python test name that contains the @cocotb.test. Usually the name of this test.
    module          = "test_sanity_check"
    # Specify what simulator to use (e.g., verilator, modelsim, icarus)
    simulator       = "verilator"
    
    run(
        includes        =include_folders,
        verilog_sources =rtl_sources,
        toplevel        =toplevel,   
        module          =module,
        simulator       =simulator,     
        sim_build       ="./sim_build/{}/".format(toplevel)
    )        
