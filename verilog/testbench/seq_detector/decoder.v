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
reg read;

reg bit_ind;
reg [3:0] last_4_bits;

reg current_state;
reg next_state;

reg [1:0] ld_current_state;
reg [1:0] ld_next_state;

reg [5:0] dot_patt = 6'b101010;
reg [7:0] long_patt = 8'b10010110;

localparam [1:0] DOT = 0;
localparam [1:0] LONG = 1;
localparam [1:0] BREAK = 2;

reg [4:0] curr_letter;

reg [4:0] out_letter;

// letter_detection ld(
//     clk,
//     read,
//     last_4_bits,
//     out_letter // as in 0-26
// );

initial begin
    current_state = IDLE;
    prev_bit = 0;
    p_prev_bit = 0;
    read = 0;
    last_4_bits = 4'b0000;
end

always_ff @(posedge clk) begin
    current_state <= next_state;
    ld_current_state <= ld_next_state;
    prev_bit <= p_prev_bit;
    last_4_bits[3] <= last_4_bits[2];
    last_4_bits[2] <= last_4_bits[1];
    last_4_bits[0] <= in_bit;
    last_4_bits[1] <= p_prev_bit;
end

always_comb begin
    next_state = current_state; // default
    ld_next_state = ld_current_state; // default
    case (current_state)
        IDLE: begin
            if (in_bit != prev_bit) begin
                next_state = DECODE;
                // read = 1;
            end
            else begin
                next_state = IDLE;
            end
        end
        DECODE: begin
            if  (out_letter != 0) begin
                next_state = IDLE;
            end
            else begin
                if (read) begin
                    case(ld_current_state)
                        DOT: begin
                            if (last_4_bits[2:0] == dot_patt[2:0] || last_4_bits[2:0] == dot_patt[5:3])
                                ld_next_state = DOT;
                            else
                                ld_next_state = LONG;
                        end
                        LONG: begin
                            if (last_4_bits == long_patt[3:0] || last_4_bits == long_patt[7:4])
                                ld_next_state = DOT;
                            else
                                ld_next_state = BREAK;
                        end
                        default: ld_next_state = DOT; // BREAK
                    endcase
                end
            end
        end
        default: begin
            next_state = IDLE;
        end
    endcase
end

always_ff @(posedge clk) begin
    if (next_state == IDLE) begin
        read <= 0;
        if (current_state == DECODE) begin
            letter_ind <= out_letter;

            if (read) begin
                case(ld_current_state)
                    DOT, LONG: begin
                        // update letter only if we aren't done
                        if (ld_next_state != BREAK) begin
                            curr_letter <= update_letter(curr_letter, ld_current_state);
                        end
                    end
                    default: begin
                        out_letter <= curr_letter; // holds until the NEXT BREAK
                        curr_letter <= 0;             // reset
                    end
                endcase
            end
        end
    end

    else if (next_state == DECODE) begin
        read <= 1;
    end

    p_prev_bit <= in_bit;
end

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
