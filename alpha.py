import numpy as np

def alpha_theo_vol(coeffs, t):
    pivot_days = 45
    pivot_time = pivot_days / 365.
    pivot_vol = coeffs[0]
    mean_vol = coeffs[1]
    alpha = coeffs[2]
    vol_t = mean_vol + (pivot_vol-mean_vol) * ( (1 - np.exp(-alpha * t)) / (1 - np.exp(-alpha * pivot_time)) ) * (pivot_time / t)
    return vol_t

