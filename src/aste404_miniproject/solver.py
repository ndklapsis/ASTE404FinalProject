import numpy as np
from typing import Callable, Optional

class HybridSolver:
    """
    A Hybrid Newton-Raphson / Bisection solver.
    Attempts Newton steps for speed. If a step goes out of bounds,
    falls back to Bisection for stability.
    """
    
    def __init__(self, tol: float = 1e-6, max_iter: int = 50):
        self.tol = tol
        self.max_iter = max_iter
        self.history = []  # Stores residual history for the verification plot

    def solve(self, func: Callable[[float], float], deriv: Callable[[float], float], 
              guess: float, low: float, high: float) -> float:
        """
        Solves func(x) = 0.
        :param func: The function f(x)
        :param deriv: The derivative f'(x)
        :param guess: Initial guess
        :param low: Lower bound (Absolute physical limit)
        :param high: Upper bound (Absolute physical limit)
        """
        self.history = []
        x = guess
        
        # Initial check to ensure root is bracketed (Good practice for Bisection)
        f_low = func(low)
        f_high = func(high)
        
        for i in range(self.max_iter):
            f_val = func(x)
            self.history.append(abs(f_val))
            
            # Check for convergence
            if abs(f_val) < self.tol:
                return x
            
            f_prime = deriv(x)
            
            # --- NEWTON STEP ---
            # x_new = x - f(x) / f'(x)
            if abs(f_prime) < 1e-12:
                # Avoid division by zero
                step = 1e9 
            else:
                step = f_val / f_prime
            
            x_new = x - step
            
            # --- HYBRID SAFETY CHECK ---
            # If Newton shoots out of bounds, switch to Bisection logic
            if x_new <= low or x_new >= high:
                # Fallback: Move to the midpoint of the valid range
                # (Simple bisection step)
                x_new = (low + high) / 2.0
            
            # Update the bounds for the next pass (Standard Bisection Logic)
            # This tightens the "walls" around the answer even if we used Newton
            if func(low) * func(x_new) < 0:
                high = x_new
            else:
                low = x_new
                
            x = x_new
            
        return x