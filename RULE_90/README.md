## FPGA Implementation Results

**Hardware:** Vicharak Shrike Lite (Renesas ForgeFPGA)

### 1. Resource Utilization

| Resource Type | Used | Total Available | Utilization % |
| :--- | :---: | :---: | :---: |
| **Logic (LUT5s)** | 280 | 1120 | **25.00%** |
| **Registers (FFs)** | 213 | 1120 | **19.02%** |
| **Block RAM** | 0 | 8 | 0.00% |
| **Global Clock Buffer**| 1 | 8 | 12.50% |

### 2. Timing Performance
F_clk = 50Mhz (utilizing internal oscillator)  
| Metric | Value |  
| :--- | :--- |    
| **Max Achievable Frequency ($F_{max}$)** | **112.54 MHz** |   
| **Min Clock Period** | 8.886 ns |    
| **Logic Depth** | 5 Stages |  
| **Setup Slack (@ 50 MHz)** | +11.11 ns |  
