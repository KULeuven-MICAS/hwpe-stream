//---------------------------------
// Copyright 2023 KULeuven
// Solderpad Hardware License, Version 0.51, see LICENSE for details.
// SPDX-License-Identifier: SHL-0.51
// Author: Ryan Antonio (ryan.antonio@esat.kuleuven.be)
//---------------------------------

module tb_hwpe_stream_demux_static #(
    //---------------------------------
    // Parameters
    //---------------------------------
    parameter NB_OUT_STREAMS = 2
);

    //---------------------------------
    // Localparameters for don't touch
    //---------------------------------
    localparam DATA_WIDTH = 32;
    localparam STRB_WIDTH = DATA_WIDTH/8;

    //---------------------------------
    // Clk and rst stimuli
    //---------------------------------
    logic clk_i, rst_ni;

    //---------------------------------
    // Interface definitions
    //---------------------------------
    // > For guidance need to check hwpe_stream_interfaces.sv
    // > Interface declarations below declare:
    // >> logic                    valid;
    // >> logic                    ready;
    // >> logic [DATA_WIDTH-1:0]   data;
    // >> logic [STRB_WIDTH-1:0]   strb;
    //
    // Note that STRB_WIDTH = DATA_WIDTH/8
    //---------------------------------

    //---------------------------------
    // Manual stimulus declaration
    //---------------------------------
    // Required for Verilator workaround
    // Note that the [0:0] mechanism for unpacked arrays is necessary for Verilator
    //---------------------------------

    logic                  push_valid_i;
    logic                  push_ready_i;
    logic [DATA_WIDTH-1:0] push_data_i;
    logic [STRB_WIDTH-1:0] push_strb_i;

    logic            [0:0] pop_valid_o [NB_OUT_STREAMS-1:0];
    logic            [0:0] pop_ready_o [NB_OUT_STREAMS-1:0]; 
    logic [DATA_WIDTH-1:0] pop_data_o  [NB_OUT_STREAMS-1:0];
    logic [STRB_WIDTH-1:0] pop_strb_o  [NB_OUT_STREAMS-1:0];

    logic                  clear_i;
    logic                  sel_i;

    //---------------------------------
    // Input interface
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) push_i (
        .clk ( clk_i )
    );

    //---------------------------------
    // Output interface
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) pop_o [NB_OUT_STREAMS-1:0] (
        .clk ( clk_i )
    );

    //---------------------------------
    // Manual mapping required by Verilator
    //---------------------------------
    assign push_i.data  =  push_data_i;
    assign push_i.valid = push_valid_i;
    assign push_i.strb  =  push_strb_i;
    assign push_ready_i =       push_i.ready;

    genvar i;
    for(i=0; i < NB_OUT_STREAMS; i++) begin
        assign pop_valid_o[i]       =       pop_o[i].valid;
        assign pop_data_o [i]       =       pop_o[i].data;
        assign pop_strb_o [i]       =       pop_o[i].strb;
        assign       pop_o[i].ready = pop_ready_o[i];
    end

    
    //---------------------------------
    // DUT
    //---------------------------------
    // 
    // push_i uses hwpe_stream_intf_stream.sink hence:
    // >> input  valid, data[DATA_WIDTH-1:0], strb[STRB_WIDTH-1:0]
    // >> output ready
    // 
    // pop_o uses hwpe_stream_intf_stream.source hence:
    // >> output valid, data[DATA_WIDTH-1:0], strb[STRB_WIDTH-1:0]
    // >> input  ready
    //---------------------------------

    hwpe_stream_demux_static  #(
        .NB_OUT_STREAMS ( NB_OUT_STREAMS )
    ) dut_hwpe_stream_demux_static (
        // Note, the clk, nrst, and clear are actually unused
        // clk and reset are used for assertion verification 
        .clk_i     ( clk_i   ),
        .rst_ni    ( rst_ni  ),
        .clear_i   ( clear_i ),
        .sel_i     ( sel_i   ),
        .push_i    ( push_i  ),
        .pop_o     ( pop_o   )
    );

endmodule