`timescale 100ms / 10ms

module tb();

reg clk;
reg enabled;
wire light;

light_manager light_instance(clk, enabled, light);

//1 Hz = 1000ms period
localparam CLK_HALF_PERIOD = 5;

initial begin
    $dumpfile("$DUMP_FILENAME");
    $dumpvars(0, tb);
    clk = 0;
    enabled = 1;
    #100;
    enabled = 0;
    #100;
    enabled = 1;
    #100;
    $finish;
end

always begin
  #CLK_HALF_PERIOD
  clk = ~clk;
end

endmodule