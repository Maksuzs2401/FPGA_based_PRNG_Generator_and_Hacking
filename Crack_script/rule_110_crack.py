from z3 import *
import time
import sys
import os
import tracemalloc 

# --- CONFIGURATION ---
FILENAME = "fpga_dump.txt"

def load_data_from_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
        
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()
            str_values = [x for x in content.split(',') if x.strip()]
            return [int(x) for x in str_values]
    except ValueError:
        print(f"Error: File '{filename}' contains non-integer data.")
        sys.exit(1)

def solve_verilog_rule110(captured_data):
    
    # 1. START MEASUREMENT
    tracemalloc.start()
    start_cpu_time = time.process_time()
    start_wall_time = time.time()
    
    s = Solver()
    
    # 1. Creating the Key
    key = BitVec('key', 64)
    
   
    s.add(Extract(63, 32, key) == 0)
    
    # 2. Building the Logic Chain
    states = [key]
    START_BIT = 29
    WINDOW_WIDTH = 4
    
    print(f"[Step 1] Building constraints for {len(captured_data)} steps...", end="")
    
    for t, observed_val in enumerate(captured_data):
        current_state = states[-1]
        
        # A. Observation Constraints
        for bit_offset in range(WINDOW_WIDTH):
            target_index = START_BIT + bit_offset
            observed_bit = (observed_val >> bit_offset) & 1
            s.add(Extract(target_index, target_index, current_state) == observed_bit)
            
        # B. (Rule 110)
        next_state = BitVec(f's_{t}', 64)
        w_right = (current_state << 1)
        w_left = LShR(current_state, 1)
        logic = (current_state ^ w_right) | (current_state & ~w_left)
        
        s.add(next_state == logic)
        states.append(next_state)

    print(" Done.")
    
    # 3. Solve
    print("[Step 2] Launching Z3 Solver")
    solve_start = time.process_time()
    
    result = s.check()
    
    solve_end = time.process_time()
    
    # 2. STOP MEASUREMENT
    end_cpu_time = time.process_time()
    end_wall_time = time.time()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # 3. CALCULATE STATS
    total_cpu_s = (end_cpu_time - start_cpu_time)
    solve_cpu_s = (solve_end - solve_start)
    peak_ram_mb = peak_mem / (1024 * 1024)

    # 4. PRINT RESULTS
    print("--------------PARAMETERS--------------")
    print(f"ATTACK TARGET:")
    print(f"  - Algorithm:     Rule 110 CA (Non-Linear)")
    print(f"  - Key Size:      64-bit (Constrained to 32-bit)")
    print(f"  - Leakage Model: 4-bit Window")
    print("-" * 42)
    print(f"PERFORMANCE:")
    print(f"  - Total CPU Time:   {total_cpu_s:.2f} s")
    print(f"  - Solver Only Time: {solve_cpu_s:.2f} s")
    print(f"  - Peak RAM Usage:   {peak_ram_mb:.2f} MB")
    print("-" * 42)
    print(f"CRYPTANALYSIS:")
    
    if result == sat:
        model = s.model()
        recovered_key = model[key].as_long()
        print(f"  - Cracked Key:    0x{recovered_key:016X}")
        print("  - Status:         [SUCCESS] Collision Found")
    else:
        print("  - Status:         [FAILURE] Unsatisfiable")
    print("==========================================")

if __name__ == "__main__":
    print(f"Reading from {FILENAME}...")
    data = load_data_from_file(FILENAME)
    solve_verilog_rule110(data)