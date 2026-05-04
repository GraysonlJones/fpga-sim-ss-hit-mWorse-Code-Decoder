`timescale 1ms / 1ms

module tb();

reg clk;
reg in_bit;
reg [4:0] let_ind;
reg [7:0] lett;

decoder decoder(
    clk, 
    in_bit, 
    let_ind
    );

get_letter gl(
    .index(let_ind),
    .letter(lett)
);

initial begin
    $dumpfile("$DUMP_FILENAME");
    $dumpvars(0, tb);
    clk = 0;

    in_bit = 0;
    #9;
    in_bit = 1;
    #4; // dot
    in_bit = 0;
    #12; // letter end - E
    in_bit = 1;
    #8; // dash
    in_bit = 0;
    #12; // letter end - T
    in_bit = 1;
    #4; // dot
    in_bit = 0;
    #8; // dash
    in_bit = 1;
    #8; // dash
    in_bit = 0;
    #4; // dot
    in_bit = 1;
    #12; // letter end - P
    in_bit = 0;
    #4; // dot
    in_bit = 1;
    #4; // dot
    in_bit = 0;
    #4; // dot
    in_bit = 1;
    #4; // dot
    in_bit = 0;
    #12; // letter end - H
    in_bit = 1;
    #8; // dash
    in_bit = 0;
    #8; // dash
    in_bit = 1;
    #8; // dash
    in_bit = 0;
    #12; // letter end - O
    in_bit = 1;
    #8; // dash
    in_bit = 0;
    #4; // dot
    in_bit = 1;
    #12; // letter end - N
    in_bit = 0;
    #4; // dot
    in_bit = 1;
    #12; // letter end - E
    
    $finish;
end

always begin
    #2;
    clk = ~clk;
end

endmodule
