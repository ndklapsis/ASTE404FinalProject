import numpy as np
from typing import Callable

class NewtonSolver:
    """Newton-Raphson solver with Bisection fallback."""
    def __init__(self, tol: float = 1e-6, max_iter: int = 50):
        self.tol = tol
        self.max_iter = max_iter
        self.history = []

    def solve(self, func: Callable, deriv: Callable, guess: float, low: float, high: float) -> float:
        self.history = []
        x = guess
        for _ in range(self.max_iter):
            f_val = func(x)
            self.history.append(abs(f_val))
            
            if abs(f_val) < self.tol: return x
            
            f_prime = deriv(x)
            if abs(f_prime) < 1e-9: step = 1e-2 # Kick if derivative is zero
            else: step = f_val / f_prime
            
            x_new = x - step
            
            # Fallback to Bisection bounds if Newton jumps out
            if x_new < low or x_new > high:
                x_new = (low + high) / 2.0
                if func(low) * func(x_new) < 0: high = x_new
                else: low = x_new
            else:
                # Update bounds for safety
                if func(low) * func(x_new) < 0: high = x_new
                else: low = x_new
            x = x_new
        return x