module prng_gen(
    input wire clk,
    input wire reset,
    input [63:0] data_in,
    input wire rx_valid_pulse, // Only step/load when this pulses
    output wire [63:0] q_out,  // SEND THIS TO SPI
    output wire led_sig
);

    reg [63:0]q;
    reg output_flag;
    wire [63:0] w_left, w_right;
    assign w_right = {q[62:0], 1'b0};
    assign w_left = {1'b0, q[63:1]};

    // Send the internal state out to the top module
    
    always @(posedge clk or negedge reset) begin
        if(!reset) begin
            q <= 64'd0;
            output_flag <= 1'b0;
        end
        else if (rx_valid_pulse) begin
            // LOGIC: If incoming data is NOT zero, load it as a SEED.
            // If incoming data IS zero, STEP the Rule 90 Automaton.
            if (data_in != 64'd0) begin
                q <= data_in; // Load Seed
            end else begin
                // Rule 110 Step
                q <= (q ^ w_right) | (q & ~w_left);
            end
            output_flag <= ~output_flag; // Toggle LED to show activity
        end
    end
    
	assign q_out = {60'd0,q[32:29]};
	assign led_sig = output_flag;

endmodule