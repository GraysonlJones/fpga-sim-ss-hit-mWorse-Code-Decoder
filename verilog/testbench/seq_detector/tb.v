`timescale 1ms / 1ms

module tb();

reg clk;
reg [2:0] in_bit;
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
    #20
    in_bit = 1;
    #5; // dot
    in_bit = 0;
    #15; // letter end - E
    in_bit = 1;
    #10; // dash
    in_bit = 0;
    #15; // letter end - T
    in_bit = 1;
    #5; // dot
    in_bit = 0;
    #10; // dash
    in_bit = 1;
    #10; // dash
    in_bit = 0;
    #5; // dot
    in_bit = 1;
    #15; // letter end - P
    in_bit = 0;
    #5; // dot
    in_bit = 1;
    #5; // dot
    in_bit = 0;
    #5; // dot
    in_bit = 1;
    #5; // dot
    in_bit = 0;
    #15; // letter end - H
    in_bit = 1;
    #10; // dash
    in_bit = 0;
    #10; // dash
    in_bit = 1;
    #10; // dash
    in_bit = 0;
    #15; // letter end - O
    in_bit = 1;
    #10; // dash
    in_bit = 0;
    #5; // dot
    in_bit = 1;
    #15; // letter end - N
    in_bit = 0;
    #5; // dot
    in_bit = 1;
    #15; // letter end - E
    


    // LETTER CONVERSION TESTING
    // let_ind = 0;
    // #2.5;
    // let_ind = 1;
    // #2.5;
    // let_ind = 2;
    // #2.5;
    // let_ind = 3;
    // #2.5;
    // let_ind = 4;
    // #2.5;
    // let_ind = 5;
    // #2.5;
    // let_ind = 6;
    // #2.5;
    // let_ind = 7;
    // #2.5;
    // let_ind = 8;
    // #2.5;
    // let_ind = 9;
    // #2.5;
    // let_ind = 10;
    // #2.5;
    // let_ind = 11;
    // #2.5;
    // let_ind = 12;
    // #2.5;
    // let_ind = 13;
    // #2.5;
    // let_ind = 14;
    // #2.5;
    // let_ind = 15;
    // #2.5;
    // let_ind = 16;
    // #2.5;
    // let_ind = 17;
    // #2.5;
    // let_ind = 18;
    // #2.5;
    // let_ind = 19;
    // #2.5;
    // let_ind = 20;
    // #2.5;
    // let_ind = 21;
    // #2.5;
    // let_ind = 22;
    // #2.5;
    // let_ind = 23;
    // #2.5;
    // let_ind = 24;
    // #2.5;
    // let_ind = 25;
    // #2.5;
    // let_ind = 26;
    // #2.5;

    // in_bit = 0;
    // #2.5;
    
    // in_bit = 1; #10;
    // in_bit = 0; #10;
    // in_bit = 1; #10;
    // in_bit = 0; #10; 
    // in_bit = 1; #10;
    // in_bit = 0; #10; 
    // in_bit = 1; #10;
    // in_bit = 0; #10; 
    // in_bit = 1; #10;
    // in_bit = 1; #10; 
    // in_bit = 0; #10;
    // in_bit = 1; #10;
    // in_bit = 0; #10; 
    $finish;
end

always begin
    #5;
    clk = ~clk;
end

endmodule
