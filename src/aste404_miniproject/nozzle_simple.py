"""
Simplified nozzle analyzer - isentropic flow only.
Loads geometry and input parameters, solves for Mach/Pressure distribution.
"""

import numpy as np
import matplotlib.pyplot as plt
from .gas_dynamics import area_mach_ratio, mach_from_area_ratio, pressure_ratio_isentropic, temperature_ratio_isentropic
from .solver import HybridSolver


class SimpleNozzleAnalyzer:
    """Analyzes nozzle flow assuming isentropic conditions throughout."""
    
    def __init__(self, x, r, Pc, Tc, gamma, Pb1):
        """
        Initialize nozzle analyzer.
        
        Args:
            x: axial positions [m]
            r: nozzle radii [m]
            Pc: chamber stagnation pressure [Pa]
            Tc: chamber stagnation temperature [K]
            gamma: specific heat ratio
            Pb1: ambient/back pressure [Pa]
        """
        self.x = np.array(x)
        self.r = np.array(r)
        self.A = np.pi * self.r**2  # Cross-sectional areas
        
        self.Pc = Pc
        self.Tc = Tc
        self.gamma = gamma
        self.Pb1 = Pb1
        
        # Find throat (minimum area)
        self.throat_idx = np.argmin(self.A)
        self.At = self.A[self.throat_idx]
        
        # Initialize solution arrays
        self.M = np.zeros_like(x, dtype=float)
        self.P = np.zeros_like(x, dtype=float)
        self.T = np.zeros_like(x, dtype=float)
    
    def solve_isentropic(self):
        """Solve for Mach number, pressure, and temperature using isentropic relations."""
        solver = HybridSolver()
        
        # Subsonic solver: M in [1e-5, 0.9999]
        subsonic_solver = HybridSolver(bounds=(1e-5, 0.9999))
        
        # Supersonic solver: M in [1.0001, 20.0]
        supersonic_solver = HybridSolver(bounds=(1.0001, 20.0))
        
        # Before throat: subsonic flow
        for i in range(self.throat_idx):
            area_ratio = self.A[i] / self.At
            
            # Define objective: |A/A_t - theoretical ratio|
            def area_error(M):
                return area_mach_ratio(M, self.gamma) - area_ratio
            
            # Solve for Mach
            self.M[i] = subsonic_solver.solve(area_error)
        
        # At throat: sonic (M = 1.0)
        self.M[self.throat_idx] = 1.0
        
        # After throat: supersonic flow
        for i in range(self.throat_idx + 1, len(self.x)):
            area_ratio = self.A[i] / self.At
            
            def area_error(M):
                return area_mach_ratio(M, self.gamma) - area_ratio
            
            # Solve for Mach
            self.M[i] = supersonic_solver.solve(area_error)
        
        # Calculate pressure and temperature from Mach
        for i in range(len(self.x)):
            P_ratio = pressure_ratio_isentropic(self.M[i], self.gamma)
            T_ratio = temperature_ratio_isentropic(self.M[i], self.gamma)
            
            self.P[i] = self.Pc * P_ratio
            self.T[i] = self.Tc * T_ratio
    
    def plot_results(self):
        """Plot Mach number and pressure distribution."""
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        
        # Mach number
        axes[0].plot(self.x, self.M, 'b-', linewidth=2, label='Mach number')
        axes[0].axhline(y=1.0, color='k', linestyle='--', alpha=0.3, label='Sonic (M=1)')
        axes[0].axvline(x=self.x[self.throat_idx], color='g', linestyle='--', alpha=0.5, label='Throat')
        axes[0].set_xlabel('Axial Position x [m]')
        axes[0].set_ylabel('Mach Number')
        axes[0].set_title('Isentropic Nozzle Flow - Mach Distribution')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        
        # Pressure
        axes[1].plot(self.x, self.P / 1000, 'r-', linewidth=2, label='Static pressure')
        axes[1].axhline(y=self.Pb1 / 1000, color='orange', linestyle='--', alpha=0.7, label=f'Ambient pressure ({self.Pb1/1000:.0f} kPa)')
        axes[1].axvline(x=self.x[self.throat_idx], color='g', linestyle='--', alpha=0.5, label='Throat')
        axes[1].set_xlabel('Axial Position x [m]')
        axes[1].set_ylabel('Static Pressure [kPa]')
        axes[1].set_title('Isentropic Nozzle Flow - Pressure Distribution')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        
        plt.tight_layout()
        plt.show()


def load_geometry(filename):
    """Load nozzle geometry from CSV file (x, r format, skip header)."""
    data = np.loadtxt(filename, delimiter=',', skiprows=1)
    return data[:, 0], data[:, 1]


def load_inputs(filename):
    """Load input parameters from text file."""
    params = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=')
                params[key.strip()] = float(value.strip())
    return params


if __name__ == "__main__":
    # Load inputs and geometry
    inputs = load_inputs('inputs/Klapsis_Nikitas_input.txt')
    x, r = load_geometry('inputs/Klapsis_Nikitas_nozzle_geometry.csv')
    
    # Create analyzer and solve
    analyzer = SimpleNozzleAnalyzer(
        x, r,
        Pc=inputs['Pc'],
        Tc=inputs['Tc'],
        gamma=inputs['gamma'],
        Pb1=inputs['Pb1']
    )
    
    analyzer.solve_isentropic()
    analyzer.plot_results()
    
    # Print summary
    print(f"Throat Mach: {analyzer.M[analyzer.throat_idx]:.6f}")
    print(f"Exit Mach: {analyzer.M[-1]:.6f}")
    print(f"Exit Pressure: {analyzer.P[-1]/1000:.2f} kPa")
    print(f"Ambient Pressure: {analyzer.Pb1/1000:.2f} kPa")
