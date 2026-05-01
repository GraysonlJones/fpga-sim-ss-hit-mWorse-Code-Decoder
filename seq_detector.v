`timescale 1ms / 1ms


// Starting state: S0

module seq_detector(
    input clk,
    input seq_in,
    output detect);

localparam S0 = 3'd0; // no match yet
localparam S1 = 3'd1; // seen "1"
localparam S2 = 3'd2; // seen "10"
localparam S3 = 3'd3; // seen "101"
localparam S4 = 3'd4; // seen "1010" 

reg [2:0] current_state;
reg [2:0] next_state;

initial begin
    current_state = S0;
end

assign detect = (current_state == S4) ? 1 : 0;

always_ff @(posedge clk) begin
    current_state = next_state;
end

always_comb begin
    if (current_state == S0) begin
        if (seq_in == 1) next_state = S1;
        else             next_state = S0;
    end
    else if (current_state == S1) begin
        if (seq_in == 0) next_state = S2;
        else             next_state = S1;
    end
    else if (current_state == S2) begin
        if (seq_in == 1) next_state = S3;
        else             next_state = S0;
    end
    else if (current_state == S3) begin
        if (seq_in == 0) next_state = S4;
        else             next_state = S1;
    end
    else begin // S4 — DETECTED
        if (seq_in == 1) next_state = S3;
        else             next_state = S0;
    end
end

endmodule
