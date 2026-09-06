from abc import ABC, abstractmethod 
import pandas as pd
import numpy as np
import warnings
from constants import c4, d2, d3, A2, A3, B3, B4, D3, D4
from rules import detect_patterns


class template_CC(ABC):
    def __init__(self, df:pd.DataFrame):
        self.data_validation(df)
        self.name()
        self.process_data(df)

    def data_validation(self, df):
        self.generic_check(df)
        self.specific_check(df)

    def generic_check(self, df):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input expected to be a pandas DataFrame")
        if df.empty:
            raise ValueError("Input DataFrame is empty")
        if df.isnull().values.any():
            raise ValueError("Input DataFrame contains NaN / missing values")
        if not np.issubdtype(df.to_numpy().dtype, np.number):
            raise TypeError("Input DataFrame must contain only numeric data types")

    @abstractmethod 
    def specific_check(self, df):
        pass

    @abstractmethod 
    def name(self):
        self.type = "placeholder"
        self.type_full = "placeholder"
        self.yaxis = "placeholder"

    @abstractmethod 
    def process_data(self, df):
        self.data = np.array()
        self.index = np.array()
        self.m = len(self.index)
        self.n = np.array()

    @abstractmethod 
    def compute_control_limits(self, pass_value = None, pass_type = None):
        self.sd = 0.0
        self.cl = 0.0
        self.lcl = np.array()
        self.ucl = np.array()

    def import_cl(self, lcl_hist, ucl_hist, cl_hist):
        self.lcl = np.full(self.m,lcl_hist)
        self.ucl = np.full(self.m,ucl_hist)
        self.cl = np.full(self.m,cl_hist)
        
    def stability(self):
        self.outside = (self.data < self.lcl) | (self.data > self.ucl)
        self.stable = not np.any(self.outside)
        self.has_pattern, self.patterns = detect_patterns(self)

    def phase1(self, pass_value = None, pass_type = None):
        self.compute_control_limits(pass_value, pass_type)
        self.stability()

    def phase2(self, lcl_hist, ucl_hist, cl_hist):
        self.import_cl(lcl_hist, ucl_hist, cl_hist)
        self.stability()


class MR(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] != 1:
            raise ValueError("Input expected to be a single column DataFrame")

    def name(self):
        self.type = "MR"
        self.type_full = "Moving Range control chart"
        self.yaxis = "Moving Range"
        

    def process_data(self, df):
        self.data = np.abs(np.diff(df.to_numpy().reshape(-1)))
        self.index = df.index[1:].to_numpy()
        self.m = len(self.data)
        self.n = 2

    def compute_control_limits(self, pass_value = None, pass_type = None):
        mean = np.mean(self.data)
        self.cl = np.full(self.m, mean)
        self.sd = self.cl / d2(self.n)
        self.lcl = np.full(self.m, mean * D3(self.n))
        self.ucl = np.full(self.m, mean * D4(self.n))



class I(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] != 1:
            raise ValueError("Input expected to be a single column DataFrame")

    def name(self):
        self.type = "I"
        self.type_full = "Individuals control chart"
        self.yaxis = "Individual Value"
        

    def process_data(self, df):
        self.data = df.to_numpy().reshape(-1)
        self.index = df.index.to_numpy()
        self.m = len(self.index)
        self.n = 1

    def compute_control_limits(self, pass_value, pass_type = None):
        mean = np.mean(self.data)
        self.cl = np.full(self.m, mean)
        self.sd = pass_value / d2(2)
        lcl = np.maximum(mean - 3 * self.sd, 0)
        self.lcl = np.full(self.m, lcl)
        self.ucl = np.full(self.m, mean + 3 * self.sd)



class R(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] < 2:
            raise ValueError("Input expected to be a DataFrame with multiple columns")
        if df.shape[1] > 10:
            warnings.warn(
                f"Subgroup size n={df.shape[1]} is more than 10. Consider using an R chart instead of an S chart.",UserWarning)

    def name(self):
        self.type = "R"
        self.type_full = "Range control chart"
        self.yaxis = "Range"

    def process_data(self, df):
        matrix = df.to_numpy()
        self.data = np.ptp(matrix, axis=1)
        self.index = df.index.to_numpy()   
        self.m = df.shape[0]
        self.n = df.shape[1]

    def compute_control_limits(self, pass_value = None, pass_type = None):
        mean = np.mean(self.data)
        self.cl = np.full(self.m, mean)
        self.sd = self.cl[0] / d2(self.n)
        self.lcl = np.full(self.m, mean * D3(self.n))
        self.ucl = np.full(self.m, mean * D4(self.n))



class S(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] < 2:
            raise ValueError("Input expected to be a DataFrame with multiple columns")
        if df.shape[1] < 10:
            warnings.warn(
                f"Subgroup size n={df.shape[1]} is less than 10. Consider using an R chart instead of an S chart.",UserWarning)

    def name(self):
        self.type = "S"
        self.type_full = "Standard Deviation control chart"
        self.yaxis = "Standard Deviation"

    def process_data(self, df):
        matrix = df.to_numpy()
        self.data = np.std(matrix, axis=1, ddof=1)
        self.index = df.index.to_numpy()   
        self.m = df.shape[0]
        self.n = df.shape[1]

    def compute_control_limits(self, pass_value = None, pass_type = None):
        mean = np.mean(self.data)
        self.cl = np.full(self.m, mean)
        self.sd = self.cl[0] / c4(self.n)
        self.lcl = np.full(self.m, mean * B3(self.n))
        self.ucl = np.full(self.m, mean * B4(self.n))



class X(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] < 2:
            raise ValueError("Input expected to be a DataFrame with multiple columns")

    def name(self):
        self.type = "X-bar"
        self.type_full = "Sample Mean control chart"
        self.yaxis = "Sample Mean"

    def process_data(self, df):
        matrix = df.to_numpy()
        self.data = np.mean(matrix, axis=1)
        self.index = df.index.to_numpy()
        self.m = df.shape[0]
        self.n = df.shape[1]

    def compute_control_limits(self, pass_value = None, pass_type = None):
        if pass_value is None or pass_type is None:
            raise ValueError("X-bar chart limits require pass_value (mean_r or mean_s) and pass_type ('R' or 'S')")
        mean = np.mean(self.data)
        self.cl = np.full(self.m, mean)
        match pass_type:
            case "R":
                self.sd = pass_value / d2(self.n)
            case "S":
                self.sd = pass_value / c4(self.n)
            case _:
                raise ValueError("pass_type must be either 'R' or 'S'")
        sd_xbar = self.sd / np.sqrt(self.n)
        self.lcl = np.full(self.m, mean - 3 * sd_xbar)
        self.ucl = np.full(self.m, mean + 3 * sd_xbar)



class C(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] != 2:
            raise ValueError("c chart requires a 2-column DataFrame (column 0: counts, column 1: sample size n)")

        matrix = df.to_numpy()
        if np.any(matrix[:, 0] < 0):
            raise ValueError("c chart counts must be non-negative")

        if np.any(matrix[:, 1] <= 0):
            raise ValueError("c chart sample sizes (n) must be strictly positive")

        if not np.all(np.isclose(matrix % 1, 0)):
            raise ValueError("c chart counts and sample sizes must be whole numbers")

        if not np.all(matrix[:, 1] == matrix[0, 1]):
            raise ValueError("c chart requires constant sample size n across all rows (use u chart)")

    def name(self):
        self.type = "c"
        self.type_full = "Count control chart"
        self.yaxis = "Count"

    def process_data(self, df):
        matrix = df.to_numpy()
        self.data = matrix[:,0] 
        self.index = df.index.to_numpy()
        self.m = len(self.index)
        self.n = matrix[:,1]

    def compute_control_limits(self, pass_value = None, pass_type = None):
        mean = np.mean(self.data)
        self.cl = np.full(self.m, mean)
        self.sd = np.sqrt(mean)
        lcl = np.maximum(mean - 3 * self.sd, 0)
        self.lcl = np.full(self.m, lcl)
        self.ucl = np.full(self.m, mean + 3 * self.sd)


class U(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] != 2:
            raise ValueError("u chart requires a 2-column DataFrame (column 0: counts, column 1: sample size n)")

        matrix = df.to_numpy()
        if np.any(matrix[:, 0] < 0):
            raise ValueError("u chart counts must be non-negative")

        if np.any(matrix[:, 1] <= 0):
            raise ValueError("u chart sample sizes (n) must be strictly positive")

        if not np.all(np.isclose(matrix % 1, 0)):
            raise ValueError("u chart counts and sample sizes must be whole numbers")

    def name(self):
        self.type = "u"
        self.type_full = "Unitised Count control chart"
        self.yaxis = "Unitised Count"

    def process_data(self, df):
        matrix = df.to_numpy()
        self.defects = matrix[:, 0]
        self.n = matrix[:, 1]
        self.data = self.defects / self.n
        self.index = df.index.to_numpy()
        self.m = len(self.index)

    def compute_control_limits(self, pass_value = None, pass_type = None):
        mean = np.sum(self.defects) / np.sum(self.n)
        self.cl = np.full(self.m, mean)
        self.sd = np.sqrt(mean/self.n)
        self.lcl = np.maximum(mean - 3 * self.sd, 0)
        self.ucl = mean + 3 * self.sd

    def import_cl(self, lcl_hist, ucl_hist, cl_hist):
        mean = cl_hist[0] if isinstance(cl_hist, np.ndarray) else cl_hist
        self.cl = np.full(self.m, mean)
        self.sd = np.sqrt(mean/self.n)
        self.lcl = np.maximum(mean - 3 * self.sd, 0)
        self.ucl = mean + 3 * self.sd


class P(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] != 2:
            raise ValueError("p chart requires a 2-column DataFrame (column 0: defectives, column 1: sample size n)")

        matrix = df.to_numpy()
        if np.any(matrix[:, 0] < 0):
            raise ValueError("p chart defectives must be non-negative")

        if np.any(matrix[:, 1] <= 0):
            raise ValueError("p chart sample sizes (n) must be strictly positive")

        if np.any(matrix[:, 0] > matrix[:, 1]):
            raise ValueError("p chart defectives cannot exceed sample size n")

        if not np.all(np.isclose(matrix % 1, 0)):
            raise ValueError("p chart defectives and sample sizes must be whole numbers")

    def name(self):
        self.type = "p"
        self.type_full = "Proportion Defective control chart"
        self.yaxis = "Proportion Defective"

    def process_data(self, df):
        matrix = df.to_numpy()
        self.defectives = matrix[:,0]
        self.n = matrix[:,1]
        self.data = self.defectives / self.n
        self.index = df.index.to_numpy()
        self.m = len(self.index)

    def compute_control_limits(self, pass_value = None, pass_type = None):
        mean = np.sum(self.defectives) / np.sum(self.n)
        self.cl = np.full(self.m, mean)
        self.sd = np.sqrt(mean*(1-mean)/self.n)
        self.lcl = np.maximum(mean - 3 * self.sd, 0)
        self.ucl = np.minimum(mean + 3 * self.sd, 1)

    def import_cl(self, lcl_hist, ucl_hist, cl_hist):
        mean = cl_hist[0] if isinstance(cl_hist, np.ndarray) else cl_hist
        self.cl = np.full(self.m, mean)
        self.sd = np.sqrt(mean*(1-mean)/self.n)
        self.lcl = np.maximum(mean - 3 * self.sd, 0)
        self.ucl = np.minimum(mean + 3 * self.sd, 1)



class NP(template_CC):
    def __init__(self, df:pd.DataFrame):
        super().__init__(df)

    def specific_check(self, df):
        if df.shape[1] != 2:
            raise ValueError("np chart requires a 2-column DataFrame (column 0: defectives, column 1: sample size n)")

        matrix = df.to_numpy()
        if np.any(matrix[:, 0] < 0):
            raise ValueError("np chart defectives must be non-negative")

        if np.any(matrix[:, 1] <= 0):
            raise ValueError("np chart sample sizes (n) must be strictly positive")

        if np.any(matrix[:, 0] > matrix[:, 1]):
            raise ValueError("np chart defectives cannot exceed sample size n")

        if not np.all(np.isclose(matrix % 1, 0)):
            raise ValueError("np chart defectives and sample sizes must be whole numbers")

        if not np.all(matrix[:, 1] == matrix[0, 1]):
            raise ValueError("np chart requires constant sample size n across all rows (use p chart)")

    def name(self):
        self.type = "np"
        self.type_full = "Number of Defectives control chart"
        self.yaxis = "Number of Defectives"

    def process_data(self, df):
        matrix = df.to_numpy()
        self.data = matrix[:,0] 
        self.index = df.index.to_numpy()
        self.m = len(self.index)
        self.n = matrix[:,1]

    def compute_control_limits(self, pass_value = None, pass_type = None):
        p = np.sum(self.data) / np.sum(self.n)
        mean = p * self.n[0]
        self.cl = np.full(self.m, mean)
        self.sd = np.sqrt(self.n * p * (1-p))
        self.lcl = np.maximum(mean - 3 * self.sd, 0)
        self.ucl = mean + 3 * self.sd