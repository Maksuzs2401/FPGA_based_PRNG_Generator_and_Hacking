# FPGA-Based Cryptanalysis of Cellular Automata PRNGs
## Introduction
This project brings the comparative analysis of safety offered by cellular automata Rule 90 and Rule 110 (AKA Turing Complete). A 64-bit PRNG was generated on Vicharak Shrike Lite FPGA board that has Renesas Forge Fpga. The .txt file then generated was used to by python script to get the master key. As a result, the master key for Rule 90 was way easy to find using simple set of linear equation due to its linear nature. Whereas, the to crack the key for Rule 110 microsoft's Z3 library was  utilized and the key had to stripped down to just 32 bits. 

## The RULE 90 and Its Cracking logic: 
### The RULE 90:
The Rule 90 on its own is just a XOR of its both neighbours, each cell is influenced by its left and right neighbourhood. 
```verilog
q <= ({q[62:0],q[63]}) ^ ({q[0],q[63:1]});
```
I have simulated that two adjacent bits of info is leaking in the transmission: 
```verilog
q_out = {62'd0,q[32:31]};
```
Ex: suppose we have a 4-bit start key: [1 0 0 0] 
in the next clock cycle we will have:    [0 1 0 1 ] (P.S. here we are operating on a cyclic shifting so neighbours of the extreme cells are not zero).
Since, the XOR operation is linear, this rule does not provide either randomness or security.

### The cracking logic:
Let's suppose the above Key [1 0 0 0] as a matrix "K". Then the output generated is:
 G =  O * K where T is a time matrix and G is the output generated matrix. Now in order to find the key we take the inverse of observability matrix and then multiply it with G.
$$K = O^{-1} G$$

SCENARIO:
```
						|k0|
					    |k1|
  - Unknown Key (K): 	|k2|
						|k3|
```
 We only see Bit 0 and Bit 1. Hence, we need 2 Clock Cycles to get 4 equations.  

**STEP 1: BUILDING THE OBSERVABILITY MATRIX (O):**  
  We stack the equations for the visible bits over time.  

  [Time T=0]  
  We see Bit 0:  $$1 \cdot k_0 + 0\cdot k_1 + 0\cdot k_2 + 0\cdot k_3$$  
  We see Bit 1:  $$0\cdot k_0 + 1\cdot k_1 + 0\cdot k_2 + 0\cdot k_3$$  

  [Time T=1]  
  New Bit 0 is (k3 ^ k1): $$0 \cdot k_0 + 1 \cdot k_1 + 0 \cdot k_2 + 1 \cdot k_3$$  
  New Bit 1 is (k0 ^ k2): $$1\cdot k_0 + 0 \cdot k_1+ 1 \cdot k_2 + 0\cdot k_3$$  

  Resulting Matrix O:
  ```
  | 1 0 0 0 | (Bit 0 @ T0)
  | 0 1 0 0 | (Bit 1 @ T0)
  | 0 1 0 1 | (Bit 0 @ T1)
  | 1 0 1 0 | (Bit 1 @ T1)
```

**STEP 2: THE LINEAR SYSTEM ($$O \cdot K = G$$)**  
  We capture data "G" from the FPGA.
  Real Key was 1000. 
  - At T=0, we saw "1" and "0".
  - At T=1, we saw "0" and "1".
  
  Captured G = [1, 0, 0, 1]

  The Equation to Solve:
  ```
  | 1 0 0 0 |    | k0 |    | 1 |
  | 0 1 0 0 | x  | k1 | =  | 0 |
  | 0 1 0 1 |    | k2 |    | 0 |
  | 1 0 1 0 |    | k3 |    | 1 | 
```

**STEP 3: GAUSSIAN ELIMINATION**  
  * Row 1: $$1 \cdot k_0 = 1$$          -> k_0 = 1
  * Row 2: $$1 \cdot k_1 = 0$$          -> k_1 = 0
  * Row 3: $$k_1 + k_3 = 0$$
           $$(0) + k_3 = 0$$            -> k_3 = 0
  * Row 4: $$k_0 + k_2 = 1$$
         $$(1) + k_2 = 1$$ 
         Subtract 1 (XOR 1)      	    -> k_2 = 0

  **RECOVERED KEY: [1, 0, 0, 0]**

> **\*Note:** here few assumptions are made, such as we already know the cell 0 & 1. In real scenario we do not know what cell info we have, but in linear system it is just few trial and error step away from the key, it might just add few seconds in computation.   

## The RULE 110 and Its Cracking logic: 
### The RULE 110:  
In this rule, we add non-linearity by using AND and OR operation. Hence, it is comparatively difficult to find the KEY and matrix operation will fail to find the correct key.  
Here, the cell is influenced by complex operations on its neighbourhood operations.  
```verilog
wire [63:0] w_left, w_right;
assign w_right = {q[62:0], 1'b0};
assign w_left = {1'b0, q[63:1]};
q = (q ^ w_right) | (q & ~w_left);
```

### The cracking logic:  

The Cracking Logic (SAT Solver): Since we cannot use a matrix inverse, we must model the system as a Boolean Logic Puzzle.   
We define the Key as a set of 64 unknown variables ($k_0, k_1, \dots, k_{63}$). We then generate thousands of logical constraints based on the captured data:  
Constraint 1: (k0 & k1) | (!k2 & k3) ... = Output_Bit_0Constraint 2: (k1 & k2) | (!k3 & k4) ... = Output_Bit_1...  
  
This creates a system of ***CNF (Conjunctive Normal Form)*** equations. To crack it, we use a ***SAT Solver (Z3)***. The solver effectively tries to "guess" values for the variables that satisfy every single constraint simultaneously.  
**Rule 90 (Linear):** Solving 64 equations takes $64^3$ operations (Milliseconds).    
**Rule 110 (Non-Linear):** This is an NP-Complete problem. The solver has to explore a decision tree that grows exponentially ($2^N$).     
**Result:** While we can crack it for small keys, a full 64-bit key would require traversing a tree so large it would take thousands of years on a normal computer.    

## Comparative Analysis:
I have performed three distinct attacks to benchmark the security of Linear vs. Non-Linear Cellular Automata.  

| Experiment Case | Target Algorithm | Attack Method | Key Size | Matrix / Model Size | CPU Time | Recovered Key | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Control Test** | **Rule 90** (Linear) | Linear Solver (Gaussian) | 64-bit | $128 \times 64$ | **0.047 s** | `0x123456789ABCDEF0` | **Success** |
| **2. Vulnerability Check** | **Rule 110** (Non-Linear) | Linear Solver (Gaussian) | 64-bit | $128 \times 64$ | **0.047 s** | `0x05B6030032CD7F3C` | **Failure** (Mismatch) |
| **3. Stress Test** | **Rule 110** (Non-Linear) | SAT Solver (Z3) | 32-bit* | N/A (Boolean Logic) | **132.31 s** | `0x000000000A8BBE49` |  **Success** |

> **\*Note:** The Rule 110 stress test was constrained to a 32-bit search space (upper 32 bits fixed to 0) to demonstrate feasibility. Unconstrained 64-bit cracking is estimated to require exponentially more time.
> In Rule 110 multiple key can result in the same bit stream generation, this is also known as collision.
$$Stream(Key_A) = Stream(Key_B)$$

## Summary
This project demonstrates that **non-linearity** is a fundamental requirement for designing secure Pseudo-Random Number Generators (PRNGs) based on Cellular Automata. 

* **Rule 90 (Linear):** We proved that linear systems are trivially vulnerable. By modeling the generator as a matrix operation, we successfully reversed the state evolution and recovered the key in milliseconds. The lack of logical complexity allows attackers to solve for the seed using standard Gaussian Elimination ($O(N^3)$).
* **Rule 110 (Non-Linear):** Conversely, the introduction of non-linear logic (AND/OR gates) effectively defeated algebraic attacks. Cracking this system required modeling it as a Boolean Satisfiability (SAT) problem, which scales exponentially in complexity ($O(2^N)$), making it computationally infeasible to break full-sized keys without vast resources.

## Future Scope
The current research relies on software-based solvers (Z3 running on a CPU). Future work will focus on **Hardware-Accelerated Cryptanalysis**:

1.  **FPGA-Based SAT Solvers:** Porting the cracking logic to high-end FPGAs (e.g., **Xilinx UltraScale+** or **Versal ACAP**).
2.  **Parallelism:** Utilizing the FPGA's DSP slices and logic cells to evaluate number of key candidates in parallel.
3.  **Pipelined Brute-Force:** Implementing a fully pipelined "Guess-and-Check" engine to drastically reduce the time-to-crack for non-linear systems, moving the attack vector from "Theoretical" to "Practical."


