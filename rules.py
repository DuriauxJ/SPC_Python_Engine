import numpy as np

def detect_patterns(chart_obj):
    sigma = (chart_obj.ucl - chart_obj.cl) / 3.0
    z_scores = np.divide((chart_obj.data - chart_obj.cl), sigma, out=np.zeros_like(chart_obj.data, dtype=float), where=sigma!=0)
    patterns = set()

    patterns.update(rule_2of3_beyond_2sigma(z_scores))
    patterns.update(rule_4of5_beyond_1sigma(z_scores))
    patterns.update(rule_same_side(z_scores))
    patterns.update(rule_trend(z_scores))
    patterns.update(rule_alternating(z_scores))
    patterns.update(rule_within_1sigma(z_scores))
    patterns.update(rule_outside_1sigma(z_scores))

    has_pattern = len(patterns) > 0
    mask_list = []

    if has_pattern:
        indices = sorted(list(patterns))
        current_chunk = [indices[0]]
        for i in indices[1:]:
            if i == current_chunk[-1] + 1:
                current_chunk.append(i)
            else:
                mask = np.zeros(chart_obj.m, dtype=bool)
                mask[current_chunk] = True
                mask_list.append(mask)
                current_chunk = [i]
        if current_chunk:
            mask = np.zeros(chart_obj.m, dtype=bool)
            mask[current_chunk] = True
            mask_list.append(mask)

    return has_pattern, mask_list

def rule_same_side(z, k=9):
    patterns = []
    for i in range(len(z) - k + 1):
        window = z[i : i+k]
        if np.all(window > 0) or np.all(window < 0):
            patterns.extend(range(i, i+k))
    return patterns

def rule_trend(z, k=6):
    patterns = []
    for i in range(len(z) - k + 1):
        window = z[i : i+k]
        diffs = np.diff(window)
        if np.all(diffs > 0) or np.all(diffs < 0):
            patterns.extend(range(i, i+k))
    return patterns

def rule_alternating(z, k=14):
    patterns = []
    for i in range(len(z) - k + 1):
        window = z[i : i+k]
        diffs = np.diff(window)
        signs = np.sign(diffs)
        products = signs[:-1] * signs[1:]     
        if np.all(products == -1):
            patterns.extend(range(i, i+k))
    return patterns

def rule_2of3_beyond_2sigma(z):
    patterns = []
    for i in range(len(z) - 2):
        window = z[i : i+3]
        if np.sum(window > 2) >= 2:
            patterns.extend(range(i, i+3))
        elif np.sum(window < -2) >= 2:
            patterns.extend(range(i, i+3))
    return patterns

def rule_4of5_beyond_1sigma(z):
    patterns = []
    for i in range(len(z) - 4):
        window = z[i : i+5]
        if np.sum(window > 1) >= 4:
            patterns.extend(range(i, i+5))
        elif np.sum(window < -1) >= 4:
            patterns.extend(range(i, i+5))
    return patterns

def rule_within_1sigma(z, k=15):
    patterns = []
    for i in range(len(z) - k + 1):
        window = z[i : i+k]
        if np.all(np.abs(window) < 1):
            patterns.extend(range(i, i+k))
    return patterns

def rule_outside_1sigma(z, k=8):
    patterns = []
    for i in range(len(z) - k + 1):
        window = z[i : i+k]
        if np.all(np.abs(window) > 1):
            patterns.extend(range(i, i+k))
    return patterns




