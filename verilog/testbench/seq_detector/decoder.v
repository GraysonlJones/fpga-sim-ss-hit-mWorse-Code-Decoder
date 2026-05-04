`timescale 1ms / 1ms

module decoder(
    input clk,
    input in_bit,
    output reg [4:0] letter_ind
);

localparam IDLE = 0;
localparam DECODE = 1;

reg prev_bit;
// reg read;

reg current_state;
reg next_state;

reg [4:0] out_letter;

letter_detection ld(
    clk,
    // read,
    in_bit,
    out_letter // as in 0-26
);

initial begin
    current_state = IDLE;
    prev_bit = 0;
    // read = 0;
end

always_ff @(posedge clk) begin
    current_state = next_state;
end

always_ff @(posedge clk) begin
    if (current_state == IDLE) begin
        if (in_bit ~^ prev_bit) begin
            next_state = DECODE;
            // read = 1;
        end
        else begin
            next_state = IDLE;
            prev_bit = in_bit;
        end
    end
    else if (out_letter != 0) begin
            next_state = IDLE;
            letter_ind = out_letter;
            // read = 0;
    end
    else begin
    	next_state = IDLE;
    end
end

endmodule
