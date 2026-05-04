`timescale 1ms / 1ms

module letter_detection(
    input clk,
    input read,
    input [3:0] last_4_bits,
    // input in_bit,
    // input prev_bit,
    output reg [4:0] output_letter
);

localparam [1:0] DOT = 0;
localparam [1:0] LONG = 1;
localparam [1:0] BREAK = 2;

reg [4:0] curr_letter;
// reg [4:0] result;

reg [1:0] current_state;
reg [1:0] next_state;
// reg activate_tree;

reg [5:0] dot_patt = 6'b101010;
reg [7:0] long_patt = 8'b10010110;
// reg [5:0] break_patt = 6'b000111;
// 101 OR 010 -> verify by ANDING - if 111 or 000, then we're good
// 001 OR 110
// 000 OR 111

initial begin
    current_state = DOT;
    curr_letter = 0;
    // result = 0;
    // activate_tree = 0;
end

always_ff @(posedge clk) begin
    current_state <= next_state;
end

always_comb begin
    next_state = current_state; // default
    if (read) begin
        case(current_state)
            DOT: begin
                if (last_4_bits[2:0] == dot_patt[2:0] || last_4_bits[2:0] == dot_patt[5:3])
                    next_state = DOT;
                else
                    next_state = LONG;
            end
            LONG: begin
                if (last_4_bits == long_patt[3:0] || last_4_bits == long_patt[7:4])
                    next_state = DOT;
                else
                    next_state = BREAK;
            end
            default: next_state = DOT; // BREAK
        endcase
    end
end

always_ff @(posedge clk) begin
    if (read) begin
        case(current_state)
            DOT, LONG: begin
                // update letter only if we aren't done
                if (next_state != BREAK) begin
                    curr_letter <= update_letter(curr_letter, current_state);
                end
            end
            default: begin
                output_letter <= curr_letter; // holds until the NEXT BREAK
                curr_letter <= 0;             // reset
            end
        endcase
    end
end

// letterTree letterTree_i(activate_tree, curr_letter, current_state, result);

// always_ff @(posedge clk) begin
//     current_state <= next_state;
// end

// always_ff @(posedge clk) begin
//     if (read) begin
//         case(current_state)
//             DOT: begin
//                 if (last_4_bits[2:0] == dot_patt[2:0] || last_4_bits[2:0] == dot_patt[5:3]) begin
//                     // activate_tree<=1;
//                     curr_letter <= update_letter(curr_letter, current_state);
//                     next_state <= DOT;
//                 end
//                 else begin
//                     next_state <= LONG;
//                 end 

//             end
//             LONG: begin
//                 if (last_4_bits == long_patt[3:0] || last_4_bits == long_patt[7:4]) begin
//                     // activate_tree <= 1;
//                     curr_letter <= update_letter(curr_letter, current_state);
//                     next_state <= DOT;
//                 end
//                 else begin
//                     next_state <= BREAK;
//                 end 
//             end
//             // BREAK: begin
//             //     next_state <= DOT;
//             //     // activate_tree <= 0;
//             //     output_letter <= curr_letter;
//             //     curr_letter <= 0;
//             // end
//             default: begin // BREAK
//                 next_state <= DOT;
//                 // activate_tree <= 0;
//                 output_letter <= curr_letter;
//                 curr_letter <= 0;
//             end
//         endcase
//     end
// end


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
