#Commands to compile in WSL 
#1) gcc -fPIC -shared -o multiplication.so multiplication.c (if not already done)
#--> This command compiles the C code in multiplication.c into a shared library named multiplication.so,
#which can then be loaded and used in Python via ctypes.
#2) python3 WCET_new.py (command to run the Python script)


import time
import random
import numpy as np
import ctypes
import os

# Loading the C library for multiplication
lib_path = os.path.abspath("./multiplication.so")
multi_lib = ctypes.CDLL(lib_path)

# Defining the input and output types for the C function
#--> uint64_t in C corresponds to c_uint64 in ctypes
multi_lib.multiply_logic.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
multi_lib.multiply_logic.restype = ctypes.c_uint64

def measure_task_1(iterations=50000):
    execution_times = []
    
    for _ in range(iterations):
        # Generation of random numbers (limited to 64 bits to match the C type)
        a = random.getrandbits(64)
        b = random.getrandbits(64)
        
        # Precise measurement of computation time
        start_time = time.perf_counter()
        
        # Calling the C function for multiplication
        multi_lib.multiply_logic(a, b)
        
        end_time = time.perf_counter()
        
        # Conversion in milliseconds (ms)
        execution_times.append((end_time - start_time) * 1000)
    
    return execution_times

# Collecting data
data = measure_task_1(50000)

# Calculating and printing the statistics
wcet = max(data)
minimum = min(data)
q1 = np.percentile(data, 25)
q2 = np.median(data)
q3 = np.percentile(data, 75)

print(f"--- Statistics for Tau 1 (via C) ---")
print(f"Min:   {minimum:.6f} ms")
print(f"Max (WCET C1): {wcet:.6f} ms")
print(f"Max with 20% margin (WCET C1): {wcet*1.2:.6f} ms")
print(f"Q1:    {q1:.6f} ms")
print(f"Q2:    {q2:.6f} ms")
print(f"Q3:    {q3:.6f} ms")