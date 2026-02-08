
## FPGA Implementation Results

**Hardware:** Vicharak Shrike Lite (Renesas ForgeFPGA)

### 1. Resource Utilization

| Resource Type | Used | Total Available | Utilization % |
| :--- | :---: | :---: | :---: |
| **Logic (LUT5s)** | 296 | 1120 | **26.43%** |
| **Registers (FFs)** | 277 | 1120 | **24.73%** |
| **Block RAM** | 0 | 8 | 0.00% |
| **Global Clock Buffer**| 1 | 8 | 12.50% |

### 2. Timing Performance
F_clk = 50 MHz (using internal oscillator)

| Metric | Value |  
| :--- | :--- |  
| **Max Achievable Frequency ($F_{max}$)** | **117.15 MHz** |  
| **Min Clock Period** | 8.536 ns |  
| **Logic Delay vs. Route Delay** | 53.5% / 46.5% |  
| **Setup Slack (@ 50 MHz)** | +11.46 ns |  
