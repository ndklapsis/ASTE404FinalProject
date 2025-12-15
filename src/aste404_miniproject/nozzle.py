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
        
        # Geometry Setup
        self.x = geometry['x'].values
        self.r = geometry['r'].values
        self.A = np.pi * self.r**2
        self.At = np.min(self.A)
        self.Ae = self.A[-1]
        self.throat_idx = np.argmin(self.A)

    def _solve_isentropic_trajectory(self, throat_choked=True):
        """
        Calculates the baseline isentropic Mach/Pressure distribution.
        If throat_choked=False, it solves the subsonic Venturi branch.
        """
        M = np.zeros_like(self.x)
        Pc = self.inputs['Pc']
        
        for i, area in enumerate(self.A):
            ratio = area / self.At
            func = lambda m: area_mach_relation(m, self.gamma) - ratio
            deriv = lambda m: area_mach_derivative(m, self.gamma)
            
            if not throat_choked:
                # Subsonic throughout (Venturi)
                # We need a boundary condition to solve this exactly, usually P_exit.
                # For this helper, we'll assume choked for the standard arrays
                # and handle pure subsonic in the specific method.
                pass 

            if i < self.throat_idx:
                # Subsonic Convergent
                M[i] = self.solver.solve(func, deriv, 0.4, 1e-5, 0.999)
            elif i == self.throat_idx:
                M[i] = 1.0
            else:
                # Supersonic Divergent
                M[i] = self.solver.solve(func, deriv, 2.5, 1.001, 10.0)
                
        P = Pc * (1 + 0.5*(self.gamma-1)*M**2)**(-self.gamma/(self.gamma-1))
        return M, P

    def _calculate_shocked_flow(self, shock_idx, M_isen):
        """
        Calculates flow with a normal shock at a specific index.
        """
        M_final = M_isen.copy()
        P_final = np.zeros_like(M_isen)
        Pc = self.inputs['Pc']
        
        # 1. Flow before shock (Isentropic)
        for i in range(shock_idx):
            P_final[i] = Pc * (1 + 0.5*(self.gamma-1)*M_final[i]**2)**(-self.gamma/(self.gamma-1))
            
        # 2. Flow across shock
        M1 = M_isen[shock_idx]
        shk = normal_shock_relations(M1, self.gamma)
        
        # New Stagnation Pressure downstream
        P0_new = Pc * shk['P02_P01']
        # New Critical Area (A_star) downstream
        At_new = self.At / shk['P02_P01']
        
        # 3. Flow after shock (Subsonic)
        for i in range(shock_idx, len(self.x)):
            ratio = self.A[i] / At_new
            func = lambda m: area_mach_relation(m, self.gamma) - ratio
            deriv = lambda m: area_mach_derivative(m, self.gamma)
            
            # Solve subsonic branch
            try:
                # If area constricts after shock, flow might re-choke (unlikely in standard nozzle)
                M_final[i] = self.solver.solve(func, deriv, 0.4, 1e-5, 0.999)
            except:
                M_final[i] = 0.0 # Error fallback
            
            P_final[i] = P0_new * (1 + 0.5*(self.gamma-1)*M_final[i]**2)**(-self.gamma/(self.gamma-1))
            
        return M_final, P_final

    def solve_with_conditions(self):
        """
        Standard single-case analyzer based on input file P_ambient.
        """
        # 1. Get Isentropic Supersonic Baseline
        M_isen, P_isen = self._solve_isentropic_trajectory()
        P_exit_design = P_isen[-1]
        P_amb = self.inputs['Pb1']
        
        self.results = {"x": self.x, "M": M_isen, "P": P_isen, "Label": "Isentropic"}

        # 2. Check Regimes
        if P_exit_design >= P_amb:
            print(f"Nozzle is Underexpanded (Pe > Pa). No internal shocks.")
            return

        # 3. Check for Normal Shock inside nozzle
        # Find the shock location that matches P_amb at exit
        best_idx = -1
        min_diff = float('inf')
        
        # Scan divergent section
        for i in range(self.throat_idx + 1, len(self.x), 5): # Step by 5 for speed
            _, P_trial = self._calculate_shocked_flow(i, M_isen)
            if abs(P_trial[-1] - P_amb) < min_diff:
                min_diff = abs(P_trial[-1] - P_amb)
                best_idx = i
        
        if best_idx != -1 and min_diff < P_amb * 0.05: # 5% Tolerance
            print(f"Normal Shock detected at x = {self.x[best_idx]:.3f} m")
            M_shock, P_shock = self._calculate_shocked_flow(best_idx, M_isen)
            self.results = {"x": self.x, "M": M_shock, "P": P_shock, "Label": "Shocked"}
        else:
            print("Flow is likely Overexpanded with Oblique Shocks outside (No internal normal shock solution found).")

    def plot_results(self):
        """Standard plot for the single analyzed case."""
        res = self.results
        fig, ax1 = plt.subplots(figsize=(10,6))
        
        ax1.set_xlabel('Axial Position (m)')
        ax1.set_ylabel('Mach Number', color='red')
        ax1.plot(res['x'], res['M'], 'r-', label=res.get('Label', 'M'))
        ax1.tick_params(axis='y', labelcolor='red')
        
        ax2 = ax1.twinx()
        ax2.set_ylabel('Pressure (Pa)', color='blue')
        ax2.plot(res['x'], res['P'], 'b--', label='Pressure')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        plt.title('Nozzle Flow Distribution')
        plt.grid(True, alpha=0.3)
        plt.show()

    def plot_pressure_sweep(self):
        """
        Generates the 'Classic' Nozzle Pressure Plot.
        Sweeps shock locations to show different regimes.
        """
        print("Generating Pressure Sweep Plot...")
        M_isen, P_isen = self._solve_isentropic_trajectory()
        
        plt.figure(figsize=(12, 7))
        
        # 1. Plot Geometry (normalized to fit plot) - Optional visualization
        # plt.fill_between(self.x, self.r/max(self.r)*max(P_isen), color='gray', alpha=0.1)

        # 2. Curve A: Design Condition (Supersonic Isentropic)
        plt.plot(self.x, P_isen / 1e5, 'k-', linewidth=2, label='Design (Supersonic)')
        
        # 3. Curve B: Shock at Exit Plane
        M_exit, P_exit_shock = self._calculate_shocked_flow(len(self.x)-1, M_isen)
        plt.plot(self.x, P_exit_shock / 1e5, 'g-', label='Shock at Exit')
        
        # 4. Curves C, D, E: Internal Shocks
        # Pick 3 locations inside the divergent section (25%, 50%, 75%)
        div_len = len(self.x) - self.throat_idx
        indices = [
            self.throat_idx + int(div_len * 0.25),
            self.throat_idx + int(div_len * 0.50),
            self.throat_idx + int(div_len * 0.75)
        ]
        
        for idx in indices:
            _, P_shk = self._calculate_shocked_flow(idx, M_isen)
            plt.plot(self.x, P_shk / 1e5, '--', label=f'Shock @ x={self.x[idx]:.2f}')