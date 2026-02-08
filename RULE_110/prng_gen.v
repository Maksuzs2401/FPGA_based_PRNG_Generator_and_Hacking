module prng_gen(
    input wire clk,
    input wire reset,
    input [63:0] data_in,
    input wire rx_valid_pulse,
    output wire [63:0] q_out,
    output wire led_sig
);

    reg [63:0] q;
    reg output_flag;

    //Creating Input Buffers
    reg [63:0] data_in_reg;
    reg rx_valid_reg;
    reg is_seed_nonzero; 

    // Pre-computing the Rule 110 Logic
    wire [63:0] w_left, w_right;
    wire [63:0] next_rule110;

    assign w_right = {q[62:0], 1'b0};
    assign w_left  = {1'b0, q[63:1]};
    
    // Rule 110: (center | right) ^ (center & left) -> This form maps better to LUT4s
    assign next_rule110 = (q ^ w_right) | (q & ~w_left);

    // Capture Inputs & Pre-Calculate the Comparator
    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            data_in_reg     <= 64'd0;
            rx_valid_reg    <= 1'b0;
            is_seed_nonzero <= 1'b0;
        end else begin
            // Register the data 
            data_in_reg  <= data_in;
            rx_valid_reg <= rx_valid_pulse;
            
            // The "|" operator (Reduction OR) checks if ANY bit is 1.
            is_seed_nonzero <= |data_in; 
        end
    end

    // Critical Path Update (Now very fast)
    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            q <= 64'd0;
            output_flag <= 1'b0;
        end 
        // Using the buffer reg for valid pulse
        else if (rx_valid_reg) begin
            // Now this "if" is just checking 1 bit (is_seed_nonzero), not 64 bits.
            if (is_seed_nonzero) begin
                q <= data_in_reg; //Load the key 
            end else begin
                q <= next_rule110; // updating the rule.
            end
            output_flag <= ~output_flag;
        end
    end
    
    assign q_out = {60'd0, q[32:29]};  //Leaking the 4 bits out of the transmission
    assign led_sig = output_flag;

endmodule
