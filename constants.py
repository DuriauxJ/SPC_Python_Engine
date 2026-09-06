from functools import lru_cache 
import numpy as np
import scipy as sp

@lru_cache
def c4(n):
    def gamma(a):
        def integrand(t):
            return t**(a-1) * np.exp(-t)
        integral, error = sp.integrate.quad(integrand,0, float("inf"))
        return integral
    return np.sqrt(2/(n-1)) * gamma(n/2) / gamma((n-1)/2)

@lru_cache
def d2(n):
    def integrand(z):
        return z * sp.stats.norm.cdf(z)**(n - 1) * sp.stats.norm.pdf(z)
    integral, error = sp.integrate.quad(integrand,-float("inf"), float("inf"))
    return 2 * n * integral

@lru_cache
def d3(n, m=50):
    nodes, weights = np.polynomial.hermite.hermgauss(m)
    def range_pdf(r):
        delta = (
            sp.stats.norm.cdf(nodes + r / 2)
            - sp.stats.norm.cdf(nodes - r / 2)
        )
        return n * (n - 1) / (2 * np.pi) * np.exp(-r**2 / 4) * np.sum(weights * delta**(n - 2))
    second_moment, _ = sp.integrate.quad(
        lambda r: r**2 * range_pdf(r),
        0,
        np.inf
    )
    return np.sqrt(second_moment - d2(n)**2)

@lru_cache
def A2(n):
    return 3 / (d2(n)*np.sqrt(n))

@lru_cache
def A3(n):
    return 3 / (c4(n)*np.sqrt(n))

@lru_cache
def B3(n):
    return max(1-3*np.sqrt(1-c4(n)**2)/c4(n), 0)

@lru_cache
def B4(n):
    return 1 + 3*np.sqrt(1-c4(n)**2)/c4(n)

@lru_cache
def D3(n):
    return max(1 - 3 * d3(n) / d2(n),0)

@lru_cache
def D4(n):
    return 1 + 3 * d3(n) / d2(n)