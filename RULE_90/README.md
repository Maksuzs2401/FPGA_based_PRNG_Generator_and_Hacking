## FPGA Implementation Results

**Hardware:** Vicharak Shrike Lite (Renesas ForgeFPGA)
**Optimization:** Pipelined Architecture for High-Frequency Stability

### 1. Resource Utilization
The design is lightweight, utilizing only 25% of the available logic, leaving ample room for future expansion.

| Resource Type | Used | Total Available | Utilization % |
| :--- | :---: | :---: | :---: |
| **Logic (LUT5s)** | 280 | 1120 | **25.00%** |
| **Registers (FFs)** | 213 | 1120 | **19.02%** |
| **Block RAM** | 0 | 8 | 0.00% |
| **Global Clock Buffer**| 1 | 8 | 12.50% |

### 2. Timing Performance
Despite targeting a standard 50 MHz board clock, the pipelined design supports frequencies up to **112.5 MHz**.

| Metric | Value | Status |
| :--- | :--- | :--- |
| **Max Achievable Frequency ($F_{max}$)** | **112.54 MHz** | 🚀 High Speed |
| **Min Clock Period** | 8.886 ns | |
| **Logic Depth** | 5 Stages | |
| **Setup Slack (@ 50 MHz)** | +11.11 ns | 🟢 **Safe** |
