`timescale 1ms / 1ms

module decoder(
    input clk,
    input [2:0] in_bit,
    output [4:0] letter_ind);

localparam [2:0] IDLE = 0;
localparam [2:0] DECODE = 1;
localparam [2:0] RESET = 2;

reg [2:0] current_state;
reg [2:0] next_state;

initial begin
    current_state = IDLE;
end

// assign new_letter = 

// always_ff @(posedge clk) begin
//     current_state = next_state;
// end

// always_comb begin
//     if (current_state == IDLE) begin
//         if (in_bit == 1) next_state = S1;
//         else             next_state = S0;
//     end
//     else if (current_state == DECODE) begin
//         if (in_bit == 0) next_state = S2;
//         else             next_state = S1;
//     end
//     else begin // RESET — DETECTED
//         if (in_bit == 1) next_state = S3;
//         else             next_state = S0;
//     end
// end

endmodule
