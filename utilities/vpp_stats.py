# VPP Statistics Utility
import numpy as np
from scipy.stats import binom

# STEP 1: Baseline data
vpp_baseline = np.array([11.9, 15, 13.6, 14.5, 14.2, 14.4, 15.6, 13.6, 13.7, 15.2, 
                             13, 13.8, 14.4, 13.3, 14, 13.3, 13.6, 15.3, 12.6, 14.8, 13.4,
                             13.2, 14.3, 13, 12.2, 14.2, 12, 14.2, 13.6, 13.8, 13.4, 14.5, 13.6])  # Replace with your 36 transducer Vpp values
n = len(vpp_baseline)
coverage = 0.95  # Desired coverage proportion
confidence = 0.95  # Desired confidence level

# STEP 2: Find minimum k such that probability >= confidence
def find_k(n, coverage, confidence):
    for k in range(n // 2 + 1):  # Max symmetric trim
        lower_tail = binom.cdf(k - 1, n, coverage)
        upper_tail = binom.cdf(k - 1, n, 1 - coverage)
        prob = 1 - lower_tail - upper_tail
        if prob >= confidence:
            return k
    raise ValueError("No k found that satisfies the tolerance condition")

k = find_k(n, coverage, confidence)
print(f"Nonparametric tolerance interval trims k = {k} values from each end")

# STEP 3: Compute the interval from sorted data
vpp_sorted = np.sort(vpp_baseline)
lower_bound = vpp_sorted[k]
upper_bound = vpp_sorted[-(k+1)]
print(f"Tolerance interval: [{lower_bound:.4f}, {upper_bound:.4f}]")

# STEP 4: Use this to check new measurements
def check_new_vpp(vpp_new):
    return lower_bound <= vpp_new <= upper_bound

