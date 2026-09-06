import numpy as np
import pandas as pd
import random
from main import SPC_run

def generate_index_special_cause(percent, m):
    number = max(round(m * percent), 1)
    return random.sample(range(0, m), number)

def generate_list_n(m, n):
    if isinstance(n, list):
        if len(n) == m:
            return n
        else:
            raise ValueError("List of provided n need to be of same length as m")
    if isinstance(n, tuple):
        if len(n) == 2:
            return random.choices(range(n[0],n[1]+1), k=m)
        else:
            raise ValueError("Provided tuple of minimum and maximum n should only contain 2 numbers")
    raise TypeError("n should be a single number, a list with the same size as m, or a tuple of minimum and maximum")



def generate_normal_data(m=25, n=5, mean=10.0, sd=1.0, special_cause_ratio=0, shift_size=2) -> pd.DataFrame:
    data = np.random.normal(loc=mean, scale=sd, size=(m, n))

    if special_cause_ratio > 0:
        if special_cause_ratio >1:
            raise ValueError("special_cause_ratio must be between 1 and 0")
        index = generate_index_special_cause(special_cause_ratio, m)
        for i in index:
            if random.choice([True, False]):
                data[i, random.choice(range(0, n))] += random.choice([-1, 1]) * shift_size * sd 
            else:
                data[i, :] += random.choice([-1, 1]) * shift_size * sd 

    return pd.DataFrame(data)

def generate_poisson_data(m=25, n=100, rate_lambda=0.05, special_cause_ratio=0, shift_rate=0.1,) -> pd.DataFrame:
    if isinstance(n, (int, float)):
        n_arr = np.full(m, round(n))
    else:
        n_arr = generate_list_n(m, n)

    rate_vector = np.full(m, rate_lambda)

    if special_cause_ratio > 0:
        if special_cause_ratio >1:
            raise ValueError("special_cause_ratio must be between 1 and 0")
        index = generate_index_special_cause(special_cause_ratio, m)
        rate_vector[index] += np.random.choice([-1, 1], size=len(index)) * shift_rate
        rate_vector = np.clip(rate_vector, a_min=0.0, a_max=None)

    counts = np.random.poisson(lam=rate_vector * n_arr)
    return pd.DataFrame({"counts": counts, "n": n_arr})

def generate_binomial_data(m=25,n=100, p=0.1, special_cause_ratio=0, shift_p=0.1) -> pd.DataFrame:
    if isinstance(n, int):
        n_arr = np.full(m, n)
    else:
        n_arr = generate_list_n(m, n)

    p_arr = np.full(m, p)

    if special_cause_ratio > 0:
        if special_cause_ratio >1:
            raise ValueError("special_cause_ratio must be between 1 and 0")
        index = generate_index_special_cause(special_cause_ratio, m)
        p_arr[index] += np.random.choice([-1, 1], size=len(index)) * shift_p
        p_arr = np.clip(p_arr, 0.0, 1.0)

    defectives = np.random.binomial(n=n_arr, p=p_arr)
    return pd.DataFrame({"defectives": defectives, "n": n_arr})

test_configs = {
    "I-MR": lambda m, sc: generate_normal_data(m=m, n=1, special_cause_ratio=sc),
    "X-R":  lambda m, sc: generate_normal_data(m=m, n=5, special_cause_ratio=sc),
    "X-S":  lambda m, sc: generate_normal_data(m=m, n=10, special_cause_ratio=sc),
    "C":    lambda m, sc: generate_poisson_data(m=m, n=100, special_cause_ratio=sc),
    "U":    lambda m, sc: generate_poisson_data(m=m, n=(50, 150), special_cause_ratio=sc),
    "P":    lambda m, sc: generate_binomial_data(m=m, n=(50, 150), special_cause_ratio=sc),
    "NP":   lambda m, sc: generate_binomial_data(m=m, n=100, special_cause_ratio=sc),
}

def run_test(m = 25, plot = True, sc_phase2 = 0.05):
    for chart_type, gen_func in test_configs.items():
        print(f"\n{'='*30}\n{chart_type} CHART TEST\n{'='*30}")

        p1_res = SPC_run(gen_func(m=m,sc=0), chart_type, plot=plot)
        chart_obj = p1_res["chart"]
        print(f"Phase 1 Return Dictionary:  {p1_res}")
    
        p2_res = SPC_run(gen_func(m=m,sc=sc_phase2), chart_type, reference=chart_obj, plot=plot)
        print(f"Phase 2 Return Dictionary: {p2_res}")

df_phase1 = generate_normal_data(m=25, n=5)

# 2. Run Phase 1 Analysis
result_p1 = SPC_run(df_phase1, "X-R", lsl=8, usl=12, plot=True)
chart_reference = result_p1["chart"]

# 3. Generate Phase 2 data with a 5% special-cause shift
df_phase2 = generate_normal_data(m=25, n=5, special_cause_ratio=0.05)

# 4. Run Phase 2 Analysis (passing Phase 1 chart limits as reference)
result_p2 = SPC_run(df_phase2, "X-R", reference=chart_reference, lsl=8, usl=12, plot=True)