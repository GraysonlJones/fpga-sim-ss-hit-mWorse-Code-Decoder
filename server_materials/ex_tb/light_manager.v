`timescale 100ms / 10ms

module light_manager(
    input clk,
    input enabled,
    output reg light)

always @(posedge clk) begin
    if(enabled) begin
        light <= ~light;
    end
    else begin
        light <= 0;
    end
end

    
endmodule
