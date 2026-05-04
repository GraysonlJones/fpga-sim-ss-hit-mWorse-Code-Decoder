`timescale 1ms / 1ms

module decoder(
    input clk,
    input in_bit,
    output reg [4:0] letter_ind
);

localparam IDLE = 0;
localparam DECODE = 1;

reg prev_bit;
reg p_prev_bit;

reg [3:0] last_4_bits;

reg current_state;
reg next_state;

reg [1:0] ld_curr_state;
reg [1:0] ld_next_state;

localparam DOT = 0;
localparam LONG = 1;

reg [4:0] curr_letter;

reg should_update_lett;

initial begin
    current_state = IDLE;
    prev_bit = 0;
    p_prev_bit = 0;
    last_4_bits = 4'b0000;
end

always_ff @(posedge clk) begin
    current_state <= next_state;
    ld_curr_state <= ld_next_state;
    prev_bit <= p_prev_bit;
    last_4_bits[3] <= last_4_bits[2];
    last_4_bits[2] <= last_4_bits[1];
    last_4_bits[0] <= in_bit;
    last_4_bits[1] <= p_prev_bit;
end

always_comb begin
    next_state = current_state;
    ld_next_state = ld_curr_state;
    should_update_lett = 0;
    if (current_state == IDLE) begin
        if (prev_bit != in_bit) begin // if there's a change in signal
            next_state = DECODE;
        end else begin
            next_state = IDLE;
        end
    end else begin // DECODE
        if (ld_curr_state == DOT) begin
            if ({last_4_bits[1:0], in_bit} == 3'b010 || {last_4_bits[1:0], in_bit} == 3'b101) begin // WE HAD A DOT (past tense)
                should_update_lett = 1;
                ld_next_state = DOT;
            end else begin
                ld_next_state = LONG;
            end
        end else begin // LONG
            if ({last_4_bits[2:0], in_bit} == 4'b0110 || {last_4_bits[2:0], in_bit} == 4'b1001) begin // WE HAD A LONG (past tense)
                should_update_lett = 1;
                ld_next_state = DOT;
            end else begin
                ld_next_state = DOT;
                next_state = IDLE;
            end
        end
    end
end

always_ff @(posedge clk) begin
    if (current_state == IDLE) begin
        // nothing...
    end else begin // DECODE
        if (should_update_lett) begin // doesn't matter which state it's in
            curr_letter <= update_letter(curr_letter, ld_curr_state);
        end else begin
            if (next_state == IDLE) begin
                letter_ind <= curr_letter;
                curr_letter <= 0;
            end
        end
    end
    
    p_prev_bit <= in_bit;
end


// update letter function
function [4:0] update_letter;
	input [4:0] currentLetterIndx;
    input [1:0] state;
	begin
        reg dorD;
        dorD = state[0];

		case (currentLetterIndx)
            5'd0:   update_letter = dorD ?    5'd20 :    5'd5;
            5'd5:   update_letter = dorD ?    5'd1  :    5'd9;
            5'd20:  update_letter = dorD ?    5'd13 :    5'd14;
            5'd9:   update_letter = dorD ?    5'd21 :    5'd19;
            5'd1:   update_letter = dorD ?    5'd23 :    5'd18;
            5'd14:  update_letter = dorD ?    5'd11 :    5'd4;
            5'd13:  update_letter = dorD ?    5'd15 :    5'd7;
            5'd19:  update_letter = dorD ?    5'd22 :    5'd8;
            5'd21:  update_letter = dorD ?    5'd0  :    5'd6;
            5'd18:  update_letter = dorD ?    5'd0  :    5'd12;
            5'd23:  update_letter = dorD ?    5'd10 :    5'd16;
            5'd4:   update_letter = dorD ?    5'd24 :    5'd2;
            5'd11:  update_letter = dorD ?    5'd25 :    5'd3;
            5'd7:   update_letter = dorD ?    5'd17 :    5'd26;
            default: update_letter = 0;
        endcase
	end
endfunction

endmodule
