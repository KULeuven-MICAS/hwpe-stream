//---------------------------------
// Copyright 2023 KULeuven
// Solderpad Hardware License, Version 0.51, see LICENSE for details.
// SPDX-License-Identifier: SHL-0.51
// Author: Ryan Antonio (ryan.antonio@esat.kuleuven.be)
//---------------------------------

module tb_hwpe_stream_fence #(
    //---------------------------------
    // Parameters
    //---------------------------------
    parameter DATA_WIDTH = 16,
    parameter NB_STREAMS = 2
);

    //---------------------------------
    // Localparameters for don't touch
    //---------------------------------
    localparam STRB_WIDTH = DATA_WIDTH/8;

    //---------------------------------
    // Clk and rst stimuli
    //---------------------------------
    logic clk_i, rst_ni;

    //---------------------------------
    // Other stimuli
    //---------------------------------
    logic clear_i;

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

    logic            [0:0] valid_i [NB_STREAMS-1:0]; 
    logic            [0:0] ready_i [NB_STREAMS-1:0]; 
    logic [DATA_WIDTH-1:0]  data_i [NB_STREAMS-1:0]; 
    logic [STRB_WIDTH-1:0]  strb_i [NB_STREAMS-1:0]; 

    logic            [0:0] valid_o [NB_STREAMS-1:0]; 
    logic            [0:0] ready_o [NB_STREAMS-1:0];
    logic [DATA_WIDTH-1:0]  data_o [NB_STREAMS-1:0];
    logic [STRB_WIDTH-1:0]  strb_o [NB_STREAMS-1:0];

    //---------------------------------
    // Input interface
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) push_i  [NB_STREAMS-1:0] (
        .clk ( clk_i )
    );

    //---------------------------------
    // Output interface
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) pop_o  [NB_STREAMS-1:0] (
        .clk ( clk_i )
    );

    //---------------------------------
    // Manual mapping required by Verilator
    //---------------------------------
    genvar i;
    for( i=0; i < NB_STREAMS; i++ ) begin
        assign valid_o[i]       =   pop_o[i].valid;
        assign  data_o[i]       =   pop_o[i].data;
        assign  strb_o[i]       =   pop_o[i].strb;
        assign   pop_o[i].ready = ready_o[i];

        assign  push_i[i].data  =  data_i[i];
        assign  push_i[i].valid = valid_i[i];
        assign  push_i[i].strb  =  strb_i[i];
        assign ready_i[i]       =  push_i[i].ready;
    end

    //---------------------------------
    // DUT
    //---------------------------------
    // push_i has multiple inputs (like an array)
    // It uses hwpe_stream_intf_stream.sink hence:
    // >> input  valid, data[DATA_WIDTH-1:0], strb[STRB_WIDTH-1:0]
    // >> output ready
    // 
    // pop_o has single output only
    // It uses hwpe_stream_intf_stream.source hence:
    // >> output valid, data[DATA_WIDTH-1:0], strb[STRB_WIDTH-1:0]
    // >> input  ready
    //---------------------------------

    hwpe_stream_fence  #(
        .NB_STREAMS   ( NB_STREAMS ),
        .DATA_WIDTH   ( DATA_WIDTH )
    ) dut_hwpe_stream_fence (
        // Note, the clk, nrst, and clear are actually unused
        // clk and reset are used for assertion verification 
        .clk_i       ( clk_i       ),
        .rst_ni      ( rst_ni      ),
        .clear_i     ( clear_i     ),
        .test_mode_i ( 1'b0        ), // Currently unused
        .push_i      ( push_i      ),
        .pop_o       ( pop_o       )
    );


endmodule