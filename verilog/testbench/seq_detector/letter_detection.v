`timescale 1ms / 1ms

module letter_detection(
    input clk,
    input read,
    input in_bit,
    output reg [4:0] output_letter
);

localparam [1:0] DOT = 0;
localparam [1:0] LONG = 1;
localparam [1:0] BREAK = 2;

reg [4:0] curr_letter;
reg a;
reg [4:0] result;

reg [1:0] current_state;
reg [1:0] next_state;
reg activate_tree;

initial begin
    current_state = DOT;
    curr_letter = 0;
    a = in_bit;
    result = 0;
    activate_tree = 0;
end

letterTree letterTree_i(activate_tree, curr_letter, current_state, result);

always_ff @(posedge clk) begin
    current_state = next_state;
end

always_comb begin
    if (read) begin
        case(current_state)
            DOT: begin
                if(in_bit == a) begin
                    next_state = LONG;
                end 
                else begin
                    activate_tree = 1;
                    curr_letter = result;
                    next_state = DOT;
                    a = in_bit;
                    activate_tree = 0;
                end
            end
            LONG: begin
                if(in_bit == a) begin
                    next_state = BREAK;
                end 
                else begin
                    activate_tree = 1;
                    curr_letter = result;
                    next_state = DOT;
                    a = in_bit;
                    activate_tree = 0;
                end
            end
            BREAK: begin
                next_state = DOT;
                output_letter = curr_letter;
                curr_letter = 0;
                a = in_bit;
            end
            default: begin
                next_state = BREAK;
                output_letter = 0;
                curr_letter = 0;
                a = in_bit;
            end
        endcase
    end
end

endmodule
