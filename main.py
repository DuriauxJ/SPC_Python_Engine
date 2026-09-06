import pandas as pd
from charts import I, MR, X, R, S, C, U, P, NP, template_CC
from assessment import assess_stability, assess_capability
from plotting import plot_CC

def SPC_run(
    df: pd.DataFrame,
    chart_type: str,  # "I-MR", "X-R", "X-S", "c", "u", "p", "np"
    reference=None,  # None for Phase 1, Phase 1 chart object or tuple for Phase 2
    lsl: float = None,
    usl: float = None,
    target: float = 1.33,
    plot: bool = True):
    dic = {}

    dic["chart"] = chart_builder(df, chart_type, reference)
    dic["stable_flag"], dic["text"], dic["pattern_flag"] = assess_stability(dic["chart"])
    if lsl is not None or usl is not None:
        dic["capability_flag"], dic["text"], dic["Cp"], dic["Cpk"] = assess_capability(dic["chart"], dic["stable_flag"], lsl, usl, target)
    if plot:
        plot_CC(dic["chart"], dic["text"])

    return dic







def chart_builder(df, chart_type, reference):
    chart_key = chart_type.upper()
    is_paired = chart_key in ["I-MR", "X-R", "X-S"]
    validate_reference(reference, is_paired)

    match chart_key:
        case "I-MR":
            mr = MR(df)
            i = I(df)
    
            if reference is None:
                mr.phase1()
                i.phase1(pass_value = mr.cl[0])
            else: 
                ref_i, ref_mr = reference
                mr.phase2(ref_mr.lcl[0], ref_mr.ucl[0], ref_mr.cl[0])
                i.phase2(ref_i.lcl[0], ref_i.ucl[0], ref_i.cl[0])

            return (i, mr)
            
        case "X-R":
            r = R(df)
            x = X(df)

            if reference is None:
                r.phase1()
                x.phase1(pass_value=r.cl[0], pass_type="R")
            else:
                ref_x, ref_r = reference
                r.phase2(ref_r.lcl[0], ref_r.ucl[0], ref_r.cl[0])
                x.phase2(ref_x.lcl[0], ref_x.ucl[0], ref_x.cl[0])

            return (x, r)
        
        case "X-S":
            s = S(df)
            x = X(df)

            if reference is None:
                s.phase1()
                x.phase1(pass_value=s.cl[0], pass_type="S")
            else:
                ref_x, ref_s = reference
                s.phase2(ref_s.lcl[0], ref_s.ucl[0], ref_s.cl[0])
                x.phase2(ref_x.lcl[0], ref_x.ucl[0], ref_x.cl[0])

            return (x, s)

        case "C" | "U" | "P" | "NP":
            chart_cls = {"C": C, "U": U, "P": P, "NP": NP}[chart_type.upper()]
            chart = chart_cls(df)
    
            if reference is None:
                chart.phase1()
            else:
                chart.phase2(reference.lcl[0], reference.ucl[0], reference.cl[0])
    
            return chart

        case _:
            raise ValueError(f"Unsupported chart type: '{chart_type}'")

def validate_reference(reference, is_paired: bool):
    if reference is None:
        return
    if is_paired:
        if not isinstance(reference, (tuple, list)) or len(reference) != 2:
            raise TypeError("For paired charts ('I-MR', 'X-R', 'X-S'), 'reference' must be a tuple of 2 chart objects: (location_chart, dispersion_chart)")
        if not (isinstance(reference[0], template_CC) and isinstance(reference[1], template_CC)):
            raise TypeError("Elements in 'reference' tuple must inherit from template_CC")
    else:
        if isinstance(reference, (tuple, list)):
            raise TypeError("For single attribute charts, 'reference' must be a single chart object")
        if not isinstance(reference, template_CC):
            raise TypeError("'reference' must be a single chart object inheriting from template_CC")







