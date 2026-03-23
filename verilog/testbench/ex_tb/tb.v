`timescale 100ms / 10ms

module tb();

reg switch_1;
reg switch_2;
wire light;

light_manager light_instance(switch_1, switch_2, light);

initial begin
    $dumpfile("$DUMP_FILENAME");
    $dumpvars(0, tb);
    switch_1 = 0;
    switch_2 = 0;
    #100;
    switch_1 = 1;
    #100;
    switch_2 = 1;
    #100;
    switch_1 = 0;
    #100;
    $finish;
end

endmodule