//---------------------------------
// Copyright 2023 KULeuven
// Solderpad Hardware License, Version 0.51, see LICENSE for details.
// SPDX-License-Identifier: SHL-0.51
// Author: Ryan Antonio (ryan.antonio@esat.kuleuven.be)
//---------------------------------

module tb_hwpe_stream_mux_static #(
    //---------------------------------
    // Parameters
    //---------------------------------
    parameter DATA_WIDTH = 32
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

    logic                  push_0_valid_i;
    logic                  push_0_ready_i;
    logic [DATA_WIDTH-1:0] push_0_data_i;
    logic [STRB_WIDTH-1:0] push_0_strb_i;

    logic                  push_1_valid_i;
    logic                  push_1_ready_i;
    logic [DATA_WIDTH-1:0] push_1_data_i;
    logic [STRB_WIDTH-1:0] push_1_strb_i;

    logic                  pop_valid_o;
    logic                  pop_ready_o;
    logic [DATA_WIDTH-1:0] pop_data_o;
    logic [STRB_WIDTH-1:0] pop_strb_o;

    logic                  clear_i;
    logic                  sel_i;

    //---------------------------------
    // Input interface
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) push_0_i (
        .clk ( clk_i )
    );

    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) push_1_i (
        .clk ( clk_i )
    );

    //---------------------------------
    // Output interface
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) pop_o (
        .clk ( clk_i )
    );

    //---------------------------------
    // Manual mapping required by Verilator
    //---------------------------------
    assign push_0_i.data  = push_0_data_i;
    assign push_0_i.valid = push_0_valid_i;
    assign push_0_i.strb  = push_0_strb_i;
    assign push_0_ready_i = push_0_i.ready;

    assign push_1_i.data  = push_1_data_i;
    assign push_1_i.valid = push_1_valid_i;
    assign push_1_i.strb  = push_1_strb_i;
    assign push_1_ready_i = push_1_i.ready;

    assign pop_valid_o = pop_o.valid;
    assign pop_data_o  = pop_o.data;
    assign pop_strb_o  = pop_o.strb;
    assign pop_o.ready = pop_ready_o;

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

    hwpe_stream_mux_static dut_hwpe_stream_mux_static (
        // Note, the clk, nrst, and clear are actually unused
        // clk and reset are used for assertion verification 
        .clk_i       ( clk_i    ),
        .rst_ni      ( rst_ni   ),
        .clear_i     ( clear_i  ),
        .sel_i       ( sel_i    ),
        .push_0_i    ( push_0_i ),
        .push_1_i    ( push_1_i ),
        .pop_o       ( pop_o    )
    );


endmodule