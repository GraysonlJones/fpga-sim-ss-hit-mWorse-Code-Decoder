`timescale 1ms / 1ms

module letterTree(
    input activate,
    input [4:0] currentLetterIndx,
    input [1:0] state,
    output reg [4:0] newLetter);

reg dorD;

assign dorD = state[0];

always @(*) begin
    if (activate) begin
        case (currentLetterIndx)
            5'd0:   newLetter = dorD ?    5'd20 :    5'd5;
            5'd5:   newLetter = dorD ?    5'd1  :    5'd9;
            5'd20:  newLetter = dorD ?    5'd13 :    5'd14;
            5'd9:   newLetter = dorD ?    5'd21 :    5'd19;
            5'd1:   newLetter = dorD ?    5'd23 :    5'd18;
            5'd14:  newLetter = dorD ?    5'd11 :    5'd4;
            5'd13:  newLetter = dorD ?    5'd15 :    5'd7;
            5'd19:  newLetter = dorD ?    5'd22 :    5'd8;
            5'd21:  newLetter = dorD ?    5'd0  :    5'd6;
            5'd18:  newLetter = dorD ?    5'd0  :    5'd12;
            5'd23:  newLetter = dorD ?    5'd10 :    5'd16;
            5'd4:   newLetter = dorD ?    5'd24 :    5'd2;
            5'd11:  newLetter = dorD ?    5'd25 :    5'd3;
            5'd7:   newLetter = dorD ?    5'd17 :    5'd26;
            default: newLetter = 0;
        endcase
    end
end

endmodule