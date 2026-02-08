module prng_gen(
    input wire clk,
    input wire reset,
    input [63:0] data_in,
    input wire rx_valid_pulse, 
    output wire [63:0] q_out,  
    output wire led_sig
);
	// Creating the Buffer regs
    reg [63:0] q, data_in_reg;
    reg output_flag;
    wire [63:0] q_new, q_left, q_right;
    reg rx_valid_buff, key_non_zero;
    
    // Pre-Computing the Rule-90 logic
    assign q_left = {q[62:0],q[63]};
    assign q_right = {q[0],q[63:1]};
    assign q_new = q_left ^ q_right;

	// Capture Inputs & Pre-Calculate the Comparator
    always @(posedge clk or negedge reset)begin
    		if(!reset)begin
    			data_in_reg <= 64'd0;
    			rx_valid_buff <= 0;
    			key_non_zero <= 0;
    		end
    		else begin
    			data_in_reg <= data_in;
    			rx_valid_buff <= rx_valid_pulse;
    			key_non_zero <= |data_in;  // The "|" operator (Reduction OR) checks if ANY bit is 1.
    		end
    end

    always @(posedge clk or negedge reset) begin
        if(!reset) begin
            q <= 64'd0;
            output_flag <= 1'b0;
        end
        else if (rx_valid_buff) begin
            
            if (key_non_zero) begin
                q <= data_in; // Load the key
            end else begin
                // Rule 90 
                q <= q_new;
            end
            output_flag <= ~output_flag; // Toggle LED
        end
    end
    
	assign q_out = {62'd0,q[32:31]};
	assign led_sig = output_flag;

endmodule
