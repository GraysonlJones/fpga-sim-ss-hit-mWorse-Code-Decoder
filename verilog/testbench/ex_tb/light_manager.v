`timescale 100ms / 10ms

module light_manager(
    input switch_1,
    input switch_2,
    output reg light);

assign light = switch_1 | switch_2;

endmodule
