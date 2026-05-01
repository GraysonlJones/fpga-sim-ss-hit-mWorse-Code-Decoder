`timescale 1ms / 1ms

module letter_detection(
    input clk,
    input in_bit,
    output reg [5:0] output_letter
);

localparam DOT = 0;
localparam LONG = 1;
localparam BREAK = 2;

reg [5:0] curr_letter;
reg a;
reg [5:0] result;

reg [1:0] current_state;
reg [1:0] next_state;

initial begin
    current_state = DOT;
    curr_letter = 0;
    a = in_bit;
    result = 0;
end

always_comb begin
    case(current_state)
        DOT: begin
            if(in_bit == a) begin
                next_state = LONG;
            end else
                letterTree letterTree_i(curr_letter, current_state, result);
                curr_letter = result;
                next_state = DOT;
                a = ~a;
            end
        end
        LONG: begin
            if(in_bit == a) begin
                next_state = BREAK;
            end else
                letterTree letterTree_i(curr_letter, current_state, result);
                curr_letter = result;
                next_state = DOT;
                a = ~a;
            end
        end
        BREAK: begin
            next_state = DOT;
            output_letter = curr_letter;
            curr_letter = 0;
            a = ~a;
        end
    endcase
end

endmodule
