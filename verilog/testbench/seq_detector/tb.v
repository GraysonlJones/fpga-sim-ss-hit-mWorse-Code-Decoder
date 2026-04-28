`timescale 1ms / 1ms

module tb();

reg clk;
reg seq_in;
wire detect;

seq_detector uut(clk, seq_in, detect);

initial begin
    $dumpfile("$DUMP_FILENAME");
    $dumpvars(0, tb);
    clk = 0;
    seq_in = 0;
    #2.5;
    // Input: 1 0 1 0 1 0 1 0 1 1 0 1 0
    // Detections expected at bits 4, 6, 8, and 13 (overlapping)
    seq_in = 1; #10;
    seq_in = 0; #10;
    seq_in = 1; #10;
    seq_in = 0; #10; 
    seq_in = 1; #10;
    seq_in = 0; #10; 
    seq_in = 1; #10;
    seq_in = 0; #10; 
    seq_in = 1; #10;
    seq_in = 1; #10; 
    seq_in = 0; #10;
    seq_in = 1; #10;
    seq_in = 0; #10; 
    $finish;
end

always begin
    #5;
    clk = ~clk;
end

endmodule
