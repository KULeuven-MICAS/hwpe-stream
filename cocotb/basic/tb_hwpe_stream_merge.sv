`define VERILATOR 1

module tb_hwpe_stream_merge #(
    //---------------------------------
    // Parameters
    //---------------------------------
    parameter DATA_WIDTH    = 8,
    parameter NB_IN_STREAMS = 2,
    parameter STRB_WIDTH    = DATA_WIDTH/8
);

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
    // Main interface
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH )
    ) push_i [NB_IN_STREAMS-1:0] (
        .clk ( clk_i )
    );

    //---------------------------------
    // Output interface
    //---------------------------------
    // Datawidth of output should be the total data widths combined
    // Merge assumes that the input data widths are consistently the same
    //---------------------------------
    hwpe_stream_intf_stream #(
        .DATA_WIDTH( DATA_WIDTH*NB_IN_STREAMS )
    ) pop_o (
        .clk ( clk_i )
    );

    //---------------------------------
    // Merge DUT
    //---------------------------------
    // push_i has multiple inputs (like an array)
    // It uses hwpe_stream_intf_stream.sink hence:
    // >> input  valid, data[DATA_WIDTh-1:0], strb[STRB_WIDTH-1:0]
    // >> output ready
    // 
    // pop_o has single output only
    // It uses hwpe_stream_intf_stream.source hence:
    // >> output valid, data[DATA_WIDTh-1:0], strb[STRB_WIDTH-1:0]
    // >> input  ready
    //---------------------------------

    hwpe_stream_merge  #(
        .NB_IN_STREAMS  ( NB_IN_STREAMS  ),
        .DATA_WIDTH_IN  ( DATA_WIDTH     )
    ) dut_hwpe_stream_merge (
        // Note, the clk, nrst, and clear are actually unused
        // clk and reset are used for assertion verification 
        .clk_i  ( clk_i   ),
        .rst_ni ( rst_ni  ),
        .clear_i( clear_i ),
        .push_i ( push_i  ),
        .pop_o  ( pop_o   )
    );

endmodule