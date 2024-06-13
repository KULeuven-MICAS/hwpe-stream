//----------------------------
// Simple sanity check counter
//----------------------------
module sanity_counter(
    input  logic        clk, 
    input  logic        reset, 
    output logic [3:0]  count
);

    logic [3:0] counter; 

    always @(posedge clk) begin
        if (reset) begin
            counter <= 0;
        end else begin
            counter <= counter + 1;
        end
    end
        
    assign count = counter;

endmodule