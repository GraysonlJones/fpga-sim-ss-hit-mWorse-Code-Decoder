`timescale 1ms / 1ms

// Starting state: S0

module get_letter(
    input [4:0] index,
    output reg [7:0] letter);

always_comb begin
    case (index)
        0: // 0
            letter = 0;
        1: 
            letter = "a";
        2:
            letter = "b";
        3:
            letter = "c";
        4:
            letter = "d";
        5:
            letter = "e";
        6:
            letter = "f";
        7:
            letter = "g";
        8:
            letter = "h";
        9:
            letter = "i";
        10:
            letter = "j";
        11:
            letter = "k";
        12:
            letter = "l";
        13:
            letter = "m";
        14:
            letter = "n";
        15:
            letter = "o";
        16:
            letter = "p";
        17:
            letter = "q";
        18:
            letter = "r";
        19:
            letter = "s";
        20:
            letter = "t";
        21:
            letter = "u";
        22:
            letter = "v";
        23:
            letter = "w";
        24:
            letter = "x";
        25:
            letter = "y";
        26:
            letter = "z";

    endcase
end


endmodule
