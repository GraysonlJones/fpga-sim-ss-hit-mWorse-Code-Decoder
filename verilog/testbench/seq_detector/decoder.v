`timescale 1ms / 1ms

module decoder(
    input clk,
    input [1:0] in_bit,
    output [4:0] letter_ind
);

localparam [1:0] IDLE = 0;
localparam [1:0] DECODE = 1;

localparam [1:0] prev_bit;

reg [2:0] current_state;
reg [2:0] next_state;

initial begin
    current_state = IDLE;
    letter_ind = 0;
end

always_ff @(posedge clk) begin
    current_state = next_state;
end

always_comb begin
    if (current_state == IDLE) begin
        if (in_bit ~^ prev_bit) next_state = DECODE;
        else begin
            next_state = IDLE;
            prev_bit = in_bit;
        end
    end
    else if (current_state == DECODE) begin
        letter_detector ld(
            clk,
            in_bit,
            out_letter // as in 0-26
        )
        if (out_letter != 0) begin
            next_state = IDLE;
            letter_ind = out_letter;
        end
    end
end

endmodule
