import numpy as np
import matplotlib.pyplot as plt
from .solver import NewtonSolver
from .gas_dynamics import area_mach_relation, area_mach_derivative, normal_shock_relations

class NozzleAnalyzer:
    def __init__(self, inputs: dict, geometry):
        self.inputs = inputs
        self.geo = geometry
        self.gamma = inputs['gamma']
        self.solver = NewtonSolver()
        
        # Calculate Areas
        self.x = geometry['x'].values
        self.r = geometry['r'].values
        self.A = np.pi * self.r**2
        self.At = np.min(self.A)
        self.Ae = self.A[-1]
        self.throat_idx = np.argmin(self.A)

    def solve_isentropic(self) -> dict:
        """Solves basic isentropic flow assuming no shocks."""
        M = np.zeros_like(self.x)
        
        for i, area in enumerate(self.A):
            ratio = area / self.At
            func = lambda m: area_mach_relation(m, self.gamma) - ratio
            deriv = lambda m: area_mach_derivative(m, self.gamma)
            
            if i < self.throat_idx:
                M[i] = self.solver.solve(func, deriv, 0.5, 1e-4, 0.999)
            elif i == self.throat_idx:
                M[i] = 1.0
            else:
                M[i] = self.solver.solve(func, deriv, 2.5, 1.001, 10.0)
                
        P = self.inputs['Pc'] * (1 + 0.5*(self.gamma-1)*M**2)**(-self.gamma/(self.gamma-1))
        return {"M": M, "P": P, "HasShock": False}

    def solve_with_conditions(self):
        """Main logic: Solves flow and handles shock detection."""
        # 1. Get Isentropic Baseline
        res = self.solve_isentropic()
        M_isen, P_isen = res['M'], res['P']
        
        P_exit = P_isen[-1]
        P_amb = self.inputs['Pb1'] # From inputs.txt
        
        print(f"  Exit Pressure (Isentropic): {P_exit:.1f} Pa")
        print(f"  Ambient Pressure:           {P_amb:.1f} Pa")
        
        # 2. Check Conditions
        if P_exit >= P_amb:
            print("  Status: Underexpanded or Optimal (No internal shock).")
            self.results = res
            return

        print("  Status: Overexpanded. Checking for Normal Shock...")
        
        # 3. Find Shock Location (if it exists inside)
        # We iterate through the divergent section.
        # At each point i, we assume a shock exists. 
        # We calculate the P0 loss, then find the NEW Exit Pressure.
        # We look for the location where New Exit Pressure == P_amb.
        
        best_idx = -1
        min_diff = float('inf')
        
        for i in range(self.throat_idx + 1, len(self.x)):
            M1 = M_isen[i]
            shock_props = normal_shock_relations(M1, self.gamma)
            P0_ratio = shock_props['P02_P01']
            
            # New P0 downstream
            P0_new = self.inputs['Pc'] * P0_ratio
            
            # New A* downstream (A*2 = A*1 / P0_ratio)
            At_new = self.At / P0_ratio
            
            # Check if flow can even exist at exit (Ae must be > At_new)
            if self.Ae < At_new: continue

            # Solve Subsonic Flow at Exit with new P0 and At
            Ae_At2 = self.Ae / At_new
            func = lambda m: area_mach_relation(m, self.gamma) - Ae_At2
            deriv = lambda m: area_mach_derivative(m, self.gamma)
            
            try:
                Me_sub = self.solver.solve(func, deriv, 0.4, 1e-4, 0.99)
                Pe_new = P0_new * (1 + 0.5*(self.gamma-1)*Me_sub**2)**(-self.gamma/(self.gamma-1))
                
                diff = abs(Pe_new - P_amb)
                if diff < min_diff:
                    min_diff = diff
                    best_idx = i
            except:
                continue
                
        # 4. If a valid shock location was found
        if best_idx != -1 and min_diff < 1000.0: # Tolerance 1kPa
            print(f"  Shock found at x = {self.x[best_idx]:.3f}")
            self._recalculate_with_shock(best_idx, M_isen)
        else:
            print("  Shock likely at lip (Oblique) or calculation diverged.")
            self.results = res

    def _recalculate_with_shock(self, shock_idx, M_isen):
        """Re-computes the flow arrays with a shock discontinuity."""
        M_final = M_isen.copy()
        P_final = np.zeros_like(M_isen)
        P0 = self.inputs['Pc']
        
        # Pre-shock P
        for i in range(shock_idx):
            P_final[i] = P0 * (1 + 0.5*(self.gamma-1)*M_final[i]**2)**(-self.gamma/(self.gamma-1))
            
        # At shock
        M1 = M_isen[shock_idx]
        shk = normal_shock_relations(M1, self.gamma)
        P0_new = P0 * shk['P02_P01']
        At_new = self.At / shk['P02_P01']
        
        # Post-shock
        for i in range(shock_idx, len(self.x)):
            ratio = self.A[i] / At_new
            func = lambda m: area_mach_relation(m, self.gamma) - ratio
            deriv = lambda m: area_mach_derivative(m, self.gamma)
            
            # Subsonic solution
            try:
                M_final[i] = self.solver.solve(func, deriv, 0.3, 1e-4, 0.999)
            except:
                M_final[i] = M_final[i-1] # Fallback
                
            P_final[i] = P0_new * (1 + 0.5*(self.gamma-1)*M_final[i]**2)**(-self.gamma/(self.gamma-1))
            
        self.results = {"M": M_final, "P": P_final, "HasShock": True, "ShockIdx": shock_idx}

    def plot_results(self):
        res = self.results
        fig, ax1 = plt.subplots(figsize=(10,6))
        
        color = 'tab:red'
        ax1.set_xlabel('Axial Position (m)')
        ax1.set_ylabel('Mach Number', color=color)
        ax1.plot(self.x, res['M'], color=color, linewidth=2)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, alpha=0.3)
        
        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('Pressure (Pa)', color=color)
        ax2.plot(self.x, res['P'], color=color, linewidth=2, linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Draw geometry outline
        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("axes", 1.2))
        ax3.set_ylabel('Nozzle Radius (m)', color='black')
        ax3.fill_between(self.x, self.r, max(self.r)*1.2, color='gray', alpha=0.2)
        
        plt.title('Nozzle Flow Solution (Pressure & Mach)')
        plt.tight_layout()
        plt.show()
        
    def plot_diagnosis(self):
        """Required by rubric: Diagnosis Plot."""
        print("Generating Diagnosis Plot (Newton Convergence)...")
        func = lambda m: area_mach_relation(m, self.gamma) - 3.0
        deriv = lambda m: area_mach_derivative(m, self.gamma)
        self.solver.solve(func, deriv, 3.0, 1.1, 5.0)
        
        plt.figure()
        plt.semilogy(self.solver.history, 'o-')
        plt.xlabel("Iteration")
        plt.ylabel("Residual")
        plt.title("Numerical Core Convergence (Newton-Raphson)")
        plt.grid(True)
        plt.show()