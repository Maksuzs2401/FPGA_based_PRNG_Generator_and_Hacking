import time
import tracemalloc 
import sys
import os

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

# --- Matrix Operations ---
def rule90_step(state_int, width=64):
    left = ((state_int << 1) | (state_int >> (width - 1))) & ((1 << width) - 1)
    right = ((state_int >> 1) | (state_int << (width - 1))) & ((1 << width) - 1)
    return left ^ right

def solve_rectangular(matrix, result_vector, n_vars=64):
    """Gaussian Elimination for Over-Defined Systems"""
    n_rows = len(matrix)
    M = [row[:] + [res] for row, res in zip(matrix, result_vector)]
    
    pivot_row = 0
    col = 0
    
    while pivot_row < n_rows and col < n_vars:
        current_row = -1
        for row in range(pivot_row, n_rows):
            if M[row][col] == 1:
                current_row = row
                break
        if current_row == -1:
            col += 1
            continue
            
        M[pivot_row], M[current_row] = M[current_row], M[pivot_row]
        for row in range(pivot_row + 1, n_rows):
            if M[row][col] == 1:
                M[row] = [a ^ b for a, b in zip(M[row], M[pivot_row])]
        pivot_row += 1
        col += 1

    solution = [0] * n_vars
    for i in range(pivot_row - 1, -1, -1):
        pivot_col = -1
        for j in range(n_vars):
            if M[i][j] == 1:
                pivot_col = j
                break
        val = M[i][-1]
        for j in range(pivot_col + 1, n_vars):
            if M[i][j] == 1:
                val ^= solution[j]
        solution[pivot_col] = val
    return solution

def main():
    
    # Parameter measurement
    tracemalloc.start()
    start_cpu_time = time.process_time()
    start_wall_time = time.time()

    # --- PROCESSING START ---
    
    print(f"[Input] Reading from {FILENAME}...")
    captured_steps = load_data_from_file(FILENAME)
    n_steps = len(captured_steps)
    print(f"[Input] Loaded {n_steps} steps of history.")

    print("[Step 1] Building Observability Matrix...")
    
    # Bit definitions
    START_BIT = 31
    WINDOW_WIDTH = 2 
    N_VARS = 64

    # Pre-calculating Basis Histories
    basis_history = []
    for i in range(N_VARS):
        history = []
        curr = (1 << i)
        for _ in range(len(captured_steps)):
            history.append(curr)
            curr = rule90_step(curr)
        basis_history.append(history)

    matrix = []
    result_vector = []

    # Building Equations
    for t, observed_val in enumerate(captured_steps):
        for bit_offset in range(WINDOW_WIDTH):
            target_bit_index = START_BIT + bit_offset
            
            # Result
            observed_bit = (observed_val >> bit_offset) & 1
            result_vector.append(observed_bit)
            
            # Coefficients
            row = []
            for k in range(N_VARS):
                state = basis_history[k][t]
                val = (state >> target_bit_index) & 1
                row.append(val)
            matrix.append(row)

    matrix_rows = len(matrix)
    print(f"[Step 2] Solving Linear System ({matrix_rows} equations for {N_VARS} unknowns)...")
    
    solve_start = time.process_time()
    recovered_bits = solve_rectangular(matrix, result_vector)
    solve_end = time.process_time()
    
    key = 0
    for i, bit in enumerate(recovered_bits):
        if bit: key |= (1 << i)

    # --- PROCESSING END ---

    end_cpu_time = time.process_time()
    end_wall_time = time.time()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 3. CALCULATE STATS
    total_cpu_ms = (end_cpu_time - start_cpu_time) * 1000
    solve_cpu_ms = (solve_end - solve_start) * 1000
    peak_ram_kb = peak_mem / 1024

    print("/n PARAMETERS")
    print(f"ATTACK TARGET:")
    print(f"  - Algorithm:     Rule 90 CA (Linear)")
    print(f"  - Key Size:      64-bit")
    print(f"  - Leakage Model: {WINDOW_WIDTH}-bit Window")
    print(f"  - Input Data:    {n_steps} samples")
    print("-" * 42)
    print(f"PERFORMANCE:")
    print(f"  - Total CPU Time:   {total_cpu_ms:.2f} ms")
    print(f"  - Solver Only Time: {solve_cpu_ms:.2f} ms")
    print(f"  - Peak RAM Usage:   {peak_ram_kb:.2f} KB")
    print("-" * 42)
    print(f"CRYPTANALYSIS:")
    print(f"  - Matrix Size:   {matrix_rows} x {N_VARS}")
    print(f"  - Cracked Key:   0x{key:016X}")
    
    # Check against the standard test key 0x123456789ABCDEF0
    if key == 0x123456789ABCDEF0:
        print("[SUCCESS]")
    else:
        # It's also a success if the key generates the same stream (Collision)
        # But for Rule 90, collisions are rare if N_Steps >= 64.
        print("[FAILURE]")

if __name__ == "__main__":
    main()