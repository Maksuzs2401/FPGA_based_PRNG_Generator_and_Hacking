module prng_gen(
    input wire clk,
    input wire reset,
    input [63:0] data_in,
    input wire rx_valid_pulse,  // data valid signal
	output wire [63:0] q_out,  // final output to the rp2040
    output wire led_sig    
);

    reg [63:0] q;
    reg output_flag;

    always @(posedge clk or negedge reset) begin
        if(!reset) begin
            q <= 64'd0;
            output_flag <= 1'b0;
        end
        else if (rx_valid_pulse) begin
            if (data_in != 64'd0) begin
				q <= data_in;     // sending the key that received from rp2040.
            end else begin
                // Rule-90
                q <= ({q[62:0],q[63]}) ^ ({q[0],q[63:1]});
            end
            output_flag <= ~output_flag; // LED toggle to show activity
        end
    end
    
	assign q_out = {62'd0,q[32:31]};           //Sending the leak signal 
	assign led_sig = output_flag;

endmodule
