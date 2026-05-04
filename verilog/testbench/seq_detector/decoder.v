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

// reg [1:0] ld_current_state;
// reg [1:0] ld_next_state;

// reg [5:0] dot_patt = 6'b101010;
// reg [7:0] long_patt = 8'b10010110;

reg [4:0] out_letter;

letter_detection ld(
    clk,
    read,
    last_4_bits,
    // in_bit,
    // prev_bit,
    out_letter // as in 0-26
);

initial begin
    current_state = IDLE;
    prev_bit = 0;
    p_prev_bit = 0;
    read = 0;
    last_4_bits = 4'b0000;
end

always_ff @(posedge clk) begin
    current_state <= next_state;
    // ld_current_state <= ld_next_state;
    prev_bit <= p_prev_bit;
    last_4_bits[3] <= last_4_bits[2];
    last_4_bits[2] <= last_4_bits[1];
    last_4_bits[0] <= in_bit;
    last_4_bits[1] <= p_prev_bit;
end

always_comb begin
    next_state = current_state; // default

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
                // read <= 0;
            end
            // else begin
                





            // end
        end
        default: begin
            next_state = IDLE;
            // read <= 0;
        end
    endcase
end

always_ff @(posedge clk) begin
    if (next_state == IDLE) begin
        if (current_state == DECODE) begin
            letter_ind <= out_letter;
        end
    end
    else if (next_state == DECODE) begin
        read <= 1;
    end

    p_prev_bit <= in_bit;
end

endmodule
