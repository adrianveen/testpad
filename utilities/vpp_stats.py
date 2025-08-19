# VPP Statistics & Outlier Detection Utility (n≈33 small-sample oriented)
import numpy as np
from scipy import stats

# Baseline Vpp measurements for the transducer (replace / refresh as needed)
vpp_baseline = np.array([
    11.9, 15.0, 13.6, 14.5, 14.2, 14.4, 15.6, 13.6, 13.7, 15.2,
    13.0, 13.8, 14.4, 13.3, 14.0, 13.3, 13.6, 15.3, 12.6, 14.8, 13.4,
    13.2, 14.3, 13.0, 12.2, 14.2, 12.0, 14.2, 13.6, 13.8, 13.4, 14.5, 13.6
])

# ---------------------------- Robust Baseline Stats ---------------------------- #

def _mad(data: np.ndarray) -> float:
    """Median Absolute Deviation (unscaled)."""
    med = np.median(data)
    return np.median(np.abs(data - med))

def compute_baseline_stats(data: np.ndarray):
    """Compute robust + classical summary statistics.

    Returns dict with:
      median, mad_raw, mad_scaled, mean, sd, n
    """
    data = np.asarray(data, float)
    n = data.size
    median = np.median(data)
    mad_raw = _mad(data)
    # Consistency constant for normal distribution
    mad_scaled = 1.4826 * mad_raw if mad_raw > 0 else 0.0
    mean = float(np.mean(data))
    sd = float(np.std(data, ddof=1)) if n > 1 else 0.0
    return dict(n=n, median=median, mad_raw=mad_raw, mad_scaled=mad_scaled, mean=mean, sd=sd)

# Pre-compute baseline stats once
_baseline = compute_baseline_stats(vpp_baseline)

def update_baseline(new_values, replace: bool = False):
    """Update the baseline dataset and recompute stats.

    Parameters
    ----------
    new_values : array-like
        New Vpp values to incorporate.
    replace : bool (default False)
        If True, replaces existing baseline entirely with new_values.
        If False, appends new_values to existing baseline.

    Returns
    -------
    dict : updated baseline stats.
    """
    global vpp_baseline, _baseline
    arr = np.asarray(new_values, float)
    if arr.size == 0:
        return _baseline
    if replace:
        vpp_baseline = arr.copy()
    else:
        vpp_baseline = np.concatenate([vpp_baseline, arr])
    _baseline = compute_baseline_stats(vpp_baseline)
    return _baseline

# ---------------------------- Prediction Intervals ---------------------------- #

def prediction_interval_t(value_stats: dict, alpha: float = 0.05):
    """Two-sided (1-alpha) prediction interval for ONE future observation
    assuming approximate normality (used as a secondary check only).
    PI: mean ± t_{1-alpha/2, n-1} * s * sqrt(1 + 1/n)
    Returns (lo, hi) or (None, None) if insufficient data.
    """
    n = value_stats['n']
    if n < 3 or value_stats['sd'] == 0:
        return (None, None)
    tcrit = stats.t.ppf(1 - alpha/2, n - 1)
    half_width = tcrit * value_stats['sd'] * np.sqrt(1 + 1/n)
    return (value_stats['mean'] - half_width, value_stats['mean'] + half_width)

# ---------------------------- Hampel (Median/MAD) Rule ---------------------------- #
# Widely used robust outlier detection. Thresholds tuned for small n.
# Classification bands (absolute robust z = |x - median| / mad_scaled):
#   <= 3.0 : OK
#   3.0 - 4.5 : SUSPECT (review / maybe re-measure)
#   > 4.5 : OUTLIER (likely invalid or abnormal)

HampelSuspectZ = 3.0
HampelOutlierZ = 4.5

def robust_z(value: float, stats_dict: dict):
    """Compute robust standardized distance (z) for a new value."""
    mad_s = stats_dict['mad_scaled']
    if mad_s == 0:  # Fallback to sd if MAD degenerates
        if stats_dict['sd'] == 0:
            return 0.0
        return (value - stats_dict['median']) / stats_dict['sd']
    return (value - stats_dict['median']) / mad_s

def classify_vpp(value: float):
    """Classify a new Vpp measurement.

    Returns dict with fields:
      value: input value
      robust_z: robust standardized distance
      classification: 'OK' | 'SUSPECT' | 'OUTLIER'
      median, mad_scaled, mean, sd, n: baseline summaries
      hampel_ok_interval: (lo, hi) interval for OK region
      prediction_interval_t: approximate parametric prediction interval (lo, hi)

    Logic:
      1. Compute robust z.
      2. Assign Hampel category.
      3. Provide parametric prediction interval for context only (not decision).
    """
    z = abs(robust_z(value, _baseline))
    if z > HampelOutlierZ:
        cls = 'OUTLIER'
    elif z >= HampelSuspectZ:
        cls = 'SUSPECT'
    else:
        cls = 'OK'

    # Hampel OK interval (symmetric about median)
    if _baseline['mad_scaled'] > 0:
        ok_half = HampelSuspectZ * _baseline['mad_scaled']
        ok_interval = (_baseline['median'] - ok_half, _baseline['median'] + ok_half)
    elif _baseline['sd'] > 0:
        ok_half = HampelSuspectZ * _baseline['sd']
        ok_interval = (_baseline['median'] - ok_half, _baseline['median'] + ok_half)
    else:
        ok_interval = (_baseline['median'], _baseline['median'])

    pi_t = prediction_interval_t(_baseline)

    return {
        'value': float(value),
        'robust_z': float(z),
        'classification': cls,
        'median': _baseline['median'],
        'mad_scaled': _baseline['mad_scaled'],
        'mean': _baseline['mean'],
        'sd': _baseline['sd'],
        'n': _baseline['n'],
        'hampel_ok_interval': ok_interval,
        'prediction_interval_t': pi_t,
    }

# Backwards compatible simple boolean (kept name but now uses Hampel OK interval)
def check_new_vpp(vpp_new: float) -> bool:
    """
    Return True only if the value is classified as 'OK' (|z| <= HampelSuspectZ).
    Eliminates edge inconsistency caused by floating point comparisons with the
    precomputed interval.
    """
    res = classify_vpp(vpp_new)
    return res['classification'] == 'OK'

# Convenience: run a short demo if executed directly
if __name__ == '__main__':
    print('Baseline summary:')
    for k, v in _baseline.items():
        print(f'  {k}: {v}')
    lo_ok, hi_ok = classify_vpp(_baseline['median'])['hampel_ok_interval']
    print(f'Hampel OK interval (|z| <= {HampelSuspectZ}): [{lo_ok:.3f}, {hi_ok:.3f}]')
    pi = prediction_interval_t(_baseline)
    if all(x is not None for x in pi):
        print(f'Parametric t prediction interval (context): [{pi[0]:.3f}, {pi[1]:.3f}]')

    test_values = [12.0, 13.5, 14.7, 16.5, 10.0]
    print('\nTest classifications:')
    for val in test_values:
        res = classify_vpp(val)
        print(f"  {val:5.2f} -> {res['classification']} (robust_z={res['robust_z']:.2f})")

    # Demonstrate updating baseline
    print('\nUpdating baseline with new values [14.1, 14.0] (append) ...')
    update_baseline([14.1, 14.0])
    print('New n:', _baseline['n'])
