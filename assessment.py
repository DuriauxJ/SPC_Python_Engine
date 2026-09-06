from charts import template_CC

def Cp(sd, lsl, usl):
    return (usl-lsl) / (6*sd)

def Cpk(mean, sd, lsl, usl):
    return min((usl-mean) / (3*sd), (mean-lsl) / (3*sd))

def compute_capability(mean, sd, lsl, usl):
    return Cp(sd, lsl, usl), Cpk(mean, sd, lsl, usl)

def capability(chart_obj: template_CC, lsl, usl, target=1.33):
    Cp, Cpk = compute_capability(chart_obj.cl[0], chart_obj.sd, lsl, usl)
    if (Cpk >= target):
        cap_text = f"The process is STABLE and CAPABLE (Cpk = {round(Cpk, 2)}"
        capable = True
    else:
        cap_text = f"The process is STABLE but NOT CAPABLE (Cpk = {round(Cpk, 2)}"
        capable = False
    return capable, Cp, Cpk, cap_text

def assess_stability(chart_obj):
    if isinstance(chart_obj, tuple):
        stable_flag = chart_obj[0].stable and chart_obj[1].stable
        pattern_flag = chart_obj[0].has_pattern or chart_obj[1].has_pattern
    else:
        stable_flag = chart_obj.stable
        pattern_flag = chart_obj.has_pattern
    text = ("The process is STABLE" if stable_flag else "The process is UNSTABLE")
    return stable_flag, text, pattern_flag

def assess_capability(chart_obj, stable_flag, lsl, usl, target):
    if not isinstance(chart_obj, tuple):
        raise TypeError("impossible to compute Cp and Cpk for c,u,p or np chart due to normality assumption")
    if lsl is None or usl is None:
        raise TypeError("Both specification limits need to be specified")
    if not stable_flag:
        return False, "The process is UNSTABLE, as such we cannot judge capability", None, None
    is_capable, Cp, Cpk, cap_text = capability(chart_obj[0], lsl, usl, target)
    return is_capable, cap_text, Cp, Cpk

    






