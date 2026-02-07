`timescale 1ns / 1ps

(* top *) module top (
    // Clock and Reset pins
    (* iopad_external_pin, clkbuf_inhibit *) input clk,
    (* iopad_external_pin *) output clk_en, 
    (* iopad_external_pin *) input rst_n,
    
    // SPI Pins
    (* iopad_external_pin *) input spi_ss_n, 
    (* iopad_external_pin *) input spi_sck, 
    (* iopad_external_pin *) input spi_mosi, 
    (* iopad_external_pin *) output spi_miso, 
    (* iopad_external_pin *) output spi_miso_en,
    
    // LED Pins
    (* iopad_external_pin *) output led, 
    (* iopad_external_pin *) output led_en 
);

    assign led_en = 1'b1;
    assign clk_en = 1'b1;

    // Internal Wires
    wire [63:0] rx_data;      
    wire        rx_valid;     
    wire [63:0] prng_out;   // Output from PRNG module
    reg         rx_valid_d;
    
    // -----------------------------------------------------------
    // 1. Valid Pulse Generation
    // 1-cycle pulse when SPI finishes receiving data
    always @(posedge clk) begin
        rx_valid_d <= rx_valid;
    end
    
    // Pulse is high only on the rising edge of valid signal
    wire valid_pulse = rx_valid & ~rx_valid_d; 

    // -----------------------------------------------------------
    // 2. SPI TARGET
    spi_target #(
        .CPOL(0), .CPHA(0), .WIDTH(64), .LSB(0)
    ) u_spi (
        .i_clk(clk), 
        .i_rst_n(rst_n),
        .i_enable(1'b1),
        .i_ss_n(spi_ss_n), .i_sck(spi_sck), .i_mosi(spi_mosi), 
        .o_miso(spi_miso), .o_miso_oe(spi_miso_en),
        .o_rx_data(rx_data),       
        .o_rx_data_valid(rx_valid),
        .i_tx_data(prng_out),    
        .o_tx_data_hold()
    );

    // -----------------------------------------------------------
    // 3. PRNG Generator
    prng_gen gen1 (
        .clk(clk),
        .reset(rst_n), 
        .data_in(rx_data),     
        .rx_valid_pulse(valid_pulse), 
        .q_out(prng_out),      
        .led_sig(led)
    );

endmodule
