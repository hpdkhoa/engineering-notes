"""
roofline_demo.py: a teaching toy for the memory versus compute (roofline) intuition behind
GPU and inference optimization. It compares naive and blocked matrix multiply, and shows the
O(n^3) growth pattern.

This is pure Python (no NumPy, no GPU), so it runs anywhere and you can see the shape of the
result. Absolute speeds do not matter here. Two things matter. Work grows about as n^3, and
better data locality (blocking) helps. The same idea makes tiled GPU matmul and good cache
behavior matter.

Run:  python3 roofline_demo.py
Deps: standard library only. It uses small sizes by default, so it finishes quickly.
"""

import time
import random

random.seed(42)


def make(n):
    return [[random.random() for _ in range(n)] for _ in range(n)]


def matmul_naive(A, B, n):
    C = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += A[i][k] * B[k][j]   # B[k][j] strides down a column, so locality is poor
            C[i][j] = s
    return C


def matmul_blocked(A, B, n, block=16):
    # Transpose B so the inner loop walks contiguous memory in both operands.
    # This is the pure Python analogue of better data locality and tiling.
    Bt = [[B[k][j] for k in range(n)] for j in range(n)]
    C = [[0.0] * n for _ in range(n)]
    for ii in range(0, n, block):
        for jj in range(0, n, block):
            for i in range(ii, min(ii + block, n)):
                Ai = A[i]
                Ci = C[i]
                for j in range(jj, min(jj + block, n)):
                    Btj = Bt[j]
                    s = 0.0
                    for k in range(n):
                        s += Ai[k] * Btj[k]   # both contiguous now
                    Ci[j] = s
    return C


def flops(n):
    return 2 * n ** 3   # one multiply and one add per inner step


print("=== O(n^3) growth: doubling n gives about 8x the work ===")
print(f"{'n':>5} | {'naive (s)':>12} | {'FLOPs':>14} | {'~time ratio':>12}")
print("-" * 52)
prev = None
for n in (32, 48, 64, 96, 128):
    A, B = make(n), make(n)
    t0 = time.perf_counter()
    matmul_naive(A, B, n)
    dt = time.perf_counter() - t0
    ratio = (dt / prev) if prev else 1.0
    print(f"{n:>5} | {dt:>12.4f} | {flops(n):>14,} | {ratio:>12.2f}x")
    prev = dt

print("\nThe time ratio tracks the (n_new/n_old)^3 work ratio. This cubic growth")
print("makes matmul the workload that GPUs and Tensor Cores exist to accelerate.\n")

print("=== Data locality: naive against locality improved (blocked and transposed) ===")
n = 96
A, B = make(n), make(n)

t0 = time.perf_counter(); matmul_naive(A, B, n);   t_naive = time.perf_counter() - t0
t0 = time.perf_counter(); matmul_blocked(A, B, n); t_block = time.perf_counter() - t0

print(f"n = {n}")
print(f"  naive            : {t_naive:.4f} s")
print(f"  locality-improved: {t_block:.4f} s")
print(f"  speedup          : {t_naive / t_block:.2f}x")
print("\nSame FLOPs with a better memory access pattern runs faster. On a GPU this is")
print("why a tiled matmul, which stages operands in fast shared memory, beats the naive")
print("version. The gain comes from moving less data. The math stays the same.")
