#include "multiplication.h"

// Simple multiplication logic using the built-in multiplication operator
uint64_t multiply_logic(uint64_t a, uint64_t b) {
    return a * b;
}

// Intensive multiplication function that performs multiple multiplications to justify the call of a C code
// 10 000 multiplications to make it intensive
uint64_t multiply_intensive(uint64_t a, uint64_t b) {
    uint64_t res = 0;
    for(int i = 0; i < 10000; i++) {
        res += (a * b);
    }
    return res;
}