import numpy as np
import matplotlib.pyplot as plt
from .solver import HybridSolver
from .gas_dynamics import (
    area_mach_relation, area_mach_derivative,
    isentropic_P_P0, isentropic_T_T0,
    normal_shock_relations, prandtl_meyer_function,
    solve_expansion_fan, solve_oblique_beta
)

class NozzleAnalyzer:
    def __init__(self, inputs: dict, geometry_df):
        self.inputs = inputs
        self.x = geometry_df['x'].values
        self.r = geometry_df['r'].values
        self.gamma = inputs['gamma']
        
        # 1. Geometry processing
        self.A = np.pi * self.r**2
        self.At = np.min(self.A) # Throat Area
        self.throat_idx = np.argmin(self.A)
        
        # Initialize the solver
        self.solver = HybridSolver()
        
        # Placeholders for results
        self.M = None
        self.P = None
        self.T = None
        self.shock_type = None  # 'normal', 'oblique', 'expansion', or None
        self.shock_location = None
        self.M_post_shock = None
        self.P_post_shock = None
        self.T_post_shock = None

    def solve_isentropic(self):
        """
        Calculates the Ideal Isentropic Flow distribution.
        """
        self.M = np.zeros_like(self.x)
        
        print(f"Solving flow for {len(self.x)} points...")
        
        for i, area in enumerate(self.A):
            # Target ratio for the solver
            target_ratio = area / self.At
            
            # Define the equation: Area_Mach(M) - Target = 0
            func = lambda m: area_mach_relation(m, self.gamma) - target_ratio
            deriv = lambda m: area_mach_derivative(m, self.gamma)
            
            # --- INTELLIGENT GUESSING ---
            if i < self.throat_idx:
                # CONVERGENT SECTION (Subsonic)
                # Bounds: Near 0 to 0.999
                self.M[i] = self.solver.solve(func, deriv, guess=0.4, low=1e-5, high=0.9999)
            
            elif i == self.throat_idx:
                # THROAT (Sonic)
                self.M[i] = 1.0
            
            else:
                # DIVERGENT SECTION (Supersonic)
                # Bounds: 1.0001 to 20.0
                self.M[i] = self.solver.solve(func, deriv, guess=2.5, low=1.0001, high=20.0)
        
        # Calculate Pressure and Temperature from Mach
        # P = Pc * (1 + (g-1)/2 * M^2)^(-g/(g-1))
        Pc = self.inputs['Pc']
        Tc = self.inputs['Tc']
        g = self.gamma
        
        self.P = isentropic_P_P0(self.M, self.gamma) * Pc
        self.T = isentropic_T_T0(self.M, self.gamma) * Tc
        
        print("Isentropic analysis complete.")
        
    def detect_shock_type(self):
        """
        Detects shock type by comparing isentropic exit pressure with ambient pressure.
        Returns: 'normal', 'oblique', 'expansion', or None
        """
        if self.M is None or self.P is None:
            print("Error: Run solve_isentropic() first.")
            return None
        
        P_exit_isen = self.P[-1]
        P_ambient = self.inputs.get('Pb1', self.inputs.get('P_ambient', 101325))  # Default to 1 atm
        
        print(f"\n--- Shock Detection Analysis ---")
        print(f"Isentropic exit pressure: {P_exit_isen/1e5:.3f} Bar")
        print(f"Ambient pressure: {P_ambient/1e5:.3f} Bar")
        
        # Exit Mach number
        M_exit_isen = self.M[-1]
        print(f"Isentropic exit Mach: {M_exit_isen:.3f}")
        
        if P_exit_isen > P_ambient:  # Underexpanded or perfectly expanded
            print("Flow regime: UNDEREXPANDED")
            # Calculate the angle of the expansion fan
            M_exit_isen = self.M[-1]
            beta = prandtl_meyer_function(M_exit_isen, self.gamma)
            print(f"Expansion fan angle (beta): {beta:.3f} degrees")
            self.shock_type = 'expansion'
            return 'expansion'
        
        elif P_exit_isen < P_ambient:  # Overexpanded
            print("Flow regime: OVEREXPANDED")
            
            # Try to find internal normal shock
            shock_idx = self._find_normal_shock_location()
            if shock_idx is not None:
                print(f"Normal shock detected at index {shock_idx} (x = {self.x[shock_idx]:.4f} m)")
                self.shock_type = 'normal'
                self.shock_location = shock_idx
                self._calculate_normal_shock_flow(shock_idx)
                return 'normal'
            else:
                print("No internal normal shock found.")
                # Calculate the angle of the oblique shock using theta-beta-M relation
                M_exit = self.M[-1]
                theta = np.arcsin(1 / M_exit)  # Approximation for small angles
                beta = np.arcsin(1 / M_exit) + np.arctan((2 * (M_exit**2 * np.sin(theta)**2 - 1)) / (M_exit**2 * (self.gamma + np.cos(2 * theta)) - 2))
                print(f"Oblique shock angle (beta): {beta:.3f} radians")
                self.shock_type = 'oblique'
                return 'oblique'
            
        else:  # Perfectly expanded
            print("Flow regime: PERFECTLY EXPANDED")
            self.shock_type = None
            return None
    
    def _find_normal_shock_location(self, tolerance=0.05):
        """
        Scan divergent section for shock location that brings exit pressure close to ambient.
        For each candidate shock location, calculate post-shock flow and check exit pressure.
        """
        P_ambient = self.inputs.get('Pb1', self.inputs.get('P_ambient', 101325))
        Pc = self.inputs['Pc']
        g = self.gamma
        
        best_idx = None
        min_error = float('inf')
        
        # Scan divergent section - check every point
        for i in range(self.throat_idx + 1, len(self.x)):
            M_before = self.M[i]
            if M_before <= 1.0:
                continue
            
            # Get shock properties at this location
            shock_data = normal_shock_relations(M_before, g)
            M_after = shock_data['M2']
            P2_P1 = shock_data['P2_P1']
            P02_P01 = shock_data['P02_P01']
            
            # Pressure before shock
            P1 = self.P[i]
            
            # New stagnation pressure after shock
            P0_new = Pc * P02_P01
            
            # Solve subsonic flow from shock to exit with new stagnation conditions
            A_exit = self.A[-1]
            A_star_new = self.At * P02_P01
            ratio_exit = A_exit / A_star_new
            
            # Find exit Mach
            func = lambda m: area_mach_relation(m, g) - ratio_exit
            deriv = lambda m: area_mach_derivative(m, g)
            
            try:
                M_exit = self.solver.solve(func, deriv, guess=0.5, low=1e-5, high=0.9999)
                # Exit pressure
                factor = 1 + 0.5 * (g - 1) * M_exit**2
                P_exit = P0_new * (factor ** (-g / (g - 1)))
            except:
                continue
            
            error = abs(P_exit - P_ambient)
            
            if error < min_error:
                min_error = error
                best_idx = i
        
        if best_idx is not None and min_error < P_ambient * tolerance:
            return best_idx
        
        return None
    
    def _calculate_normal_shock_flow(self, shock_idx):
        """
        Recalculates the flow field with a normal shock at shock_idx.
        Stores results in M_post_shock, P_post_shock, T_post_shock.
        """
        self.M_post_shock = self.M.copy()
        self.P_post_shock = np.zeros_like(self.P)
        self.T_post_shock = np.zeros_like(self.T)
        
        Pc = self.inputs['Pc']
        Tc = self.inputs['Tc']
        g = self.gamma
        
        # 1. Before shock: copy isentropic values
        for i in range(shock_idx):
            self.P_post_shock[i] = self.P[i]
            self.T_post_shock[i] = self.T[i]
        
        # 2. Across shock
        M1 = self.M[shock_idx]
        shock_data = normal_shock_relations(M1, g)
        M2 = shock_data['M2']
        P2_P1 = shock_data['P2_P1']
        P02_P01 = shock_data['P02_P01']
        
        P1 = self.P[shock_idx]
        P2 = P1 * P2_P1
        T1 = self.T[shock_idx]
        
        # Temperature after shock
        temp_ratio = (P2/P1) * (2/(g+1)) / (1 + ((g-1)/(g+1)) * (P2/P1))
        T2 = T1 * temp_ratio
        
        # New stagnation conditions downstream of shock
        P0_new = Pc * P02_P01
        T0_new = Tc  # Stagnation temperature constant through shock
        
        # New effective critical area
        A_star_new = self.At * P02_P01
        
        self.M_post_shock[shock_idx] = M2
        self.P_post_shock[shock_idx] = P2
        self.T_post_shock[shock_idx] = T2
        
        # 3. After shock: subsonic isentropic flow in divergent section
        for i in range(shock_idx + 1, len(self.x)):
            area = self.A[i]
            ratio = area / A_star_new
            
            func = lambda m: area_mach_relation(m, g) - ratio
            deriv = lambda m: area_mach_derivative(m, g)
            
            try:
                self.M_post_shock[i] = self.solver.solve(func, deriv, guess=0.5, low=1e-5, high=0.9999)
            except:
                self.M_post_shock[i] = 0.01  # Fallback to low Mach
            
            # Pressure after shock (using new stagnation values)
            factor = 1 + 0.5 * (g - 1) * self.M_post_shock[i]**2
            self.P_post_shock[i] = P0_new * (factor ** (-g / (g - 1)))
            self.T_post_shock[i] = T0_new * (factor ** -1)
        
        print(f"Normal shock calculation complete at index {shock_idx}")
        print(f"  Pre-shock Mach: {M1:.3f}, Post-shock Mach: {M2:.3f}")
        print(f"  Pressure ratio P2/P1: {P2_P1:.3f}")
        print(f"  Stagnation pressure ratio P02/P01: {P02_P01:.3f}")
        print(f"  Exit pressure with shock: {self.P_post_shock[-1]/1e5:.3f} Bar")

    def plot_results(self):
        """Generates detailed plots of the nozzle analysis with shock detection results."""
        if self.M is None:
            print("Error: Run solve_isentropic() and detect_shock_type() first.")
            return

        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        
        # Create grid for subplots - larger nozzle plot
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3, height_ratios=[2.5, 1, 1])
        ax1 = fig.add_subplot(gs[0, :])    # Nozzle contour with Mach overlay (full width, large)
        ax2 = fig.add_subplot(gs[1, :])    # Pressure (full width)
        ax3 = fig.add_subplot(gs[2, 0])    # Temperature
        ax5 = fig.add_subplot(gs[2, 1])    # Solver convergence (error over iteration)
        ax4 = fig.add_subplot(gs[2, 2])    # Shock info text
        
        # --- Plot 1: Nozzle Contour with Mach Heatmap (Large at TOP) ---
        self._plot_nozzle_contour(ax1)
        
        # --- Plot 2: Pressure ---
        ax2.plot(self.x, self.P / 1e5, 'b-', linewidth=2.5, label='Isentropic')
        
        if self.shock_type == 'normal' and self.P_post_shock is not None:
            ax2.plot(self.x, self.P_post_shock / 1e5, 'g--', linewidth=2, label='With Normal Shock')
            if self.shock_location is not None:
                ax2.axvline(self.x[self.shock_location], color='orange', linestyle=':', linewidth=2)
                ax2.plot(self.x[self.shock_location], self.P[self.shock_location] / 1e5, 'bo', markersize=8)
                ax2.plot(self.x[self.shock_location], self.P_post_shock[self.shock_location] / 1e5, 'go', markersize=8)
        
        # Show ambient pressure
        P_ambient = self.inputs.get('Pb1', self.inputs.get('P_ambient', 101325))
        ax2.axhline(P_ambient / 1e5, color='gray', linestyle='--', linewidth=1.5, label=f'Ambient ({P_ambient/1e5:.3f} Bar)')
        
        ax2.set_ylabel('Pressure (Bar)', fontsize=11, fontweight='bold', color='blue')
        ax2.set_xlabel('Axial Position x (m)', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best')
        
        # --- Plot 3: Temperature ---
        ax3.plot(self.x, self.T, 'purple', linewidth=2.5, label='Isentropic')
        
        if self.shock_type == 'normal' and self.T_post_shock is not None:
            ax3.plot(self.x, self.T_post_shock, 'brown', linestyle='--', linewidth=2, label='With Normal Shock')
            if self.shock_location is not None:
                ax3.axvline(self.x[self.shock_location], color='orange', linestyle=':', linewidth=1.5)
        
        ax3.set_ylabel('Temperature (K)', fontsize=10, fontweight='bold')
        ax3.set_xlabel('Axial Position x (m)', fontsize=10, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='best')
        
        # --- Plot 5: Solver Convergence (Error Over Iterations) ---
        if self.solver.history:
            iterations = range(1, len(self.solver.history) + 1)
            ax5.semilogy(iterations, self.solver.history, 'r.-', linewidth=2, markersize=6)
            ax5.set_ylabel('Absolute Error |f(x)|', fontsize=10, fontweight='bold')
            ax5.set_xlabel('Iteration', fontsize=10, fontweight='bold')
            ax5.set_title('Solver Convergence', fontsize=11, fontweight='bold')
            ax5.grid(True, alpha=0.3, which='both')
            ax5.axhline(self.solver.tol, color='green', linestyle='--', linewidth=1.5, label=f'Tolerance ({self.solver.tol:.0e})')
            ax5.legend(loc='best', fontsize=9)
        
        # --- Plot 4: Summary Text ---
        ax4.axis('off')
        summary_text = self._generate_shock_summary()
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.show()
    
    def _generate_shock_summary(self):
        """Generates a text summary of the shock detection results."""
        P_ambient = self.inputs.get('Pb1', self.inputs.get('P_ambient', 101325))
        
        summary = "=== SHOCK ANALYSIS SUMMARY ===\n\n"
        summary += f"Shock Type: {self.shock_type.upper() if self.shock_type else 'NONE'}\n"
        summary += f"Ambient Pressure: {P_ambient/1e5:.3f} Bar\n\n"
        
        # Isentropic conditions
        summary += "ISENTROPIC (Design):\n"
        summary += f"  Exit Mach: {self.M[-1]:.3f}\n"
        summary += f"  Exit Pressure: {self.P[-1]/1e5:.3f} Bar\n"
        summary += f"  Exit Temp: {self.T[-1]:.1f} K\n"
        summary += f"  Pressure Deficit: {(self.P[-1] - P_ambient)/1e5:.3f} Bar\n\n"
        
        # Post-shock conditions (if applicable)
        if self.shock_type == 'normal' and self.M_post_shock is not None:
            summary += "WITH NORMAL SHOCK:\n"
            summary += f"  Shock Location: x = {self.x[self.shock_location]:.4f} m\n"
            summary += f"  Pre-shock Mach: {self.M[self.shock_location]:.3f}\n"
            summary += f"  Post-shock Mach: {self.M_post_shock[self.shock_location]:.3f}\n"
            summary += f"  Exit Mach: {self.M_post_shock[-1]:.3f}\n"
            summary += f"  Exit Pressure: {self.P_post_shock[-1]/1e5:.3f} Bar\n"
            summary += f"  Pressure Error: {abs(self.P_post_shock[-1] - P_ambient)/P_ambient*100:.1f}%\n"
        elif self.shock_type == 'oblique':
            summary += "OBLIQUE SHOCK SYSTEM:\n"
            summary += f"  Exit Mach (supersonic): {self.M[-1]:.3f}\n"
            summary += f"  Exit pressure (overexpanded):\n"
            summary += f"    {self.P[-1]/1e5:.3f} Bar << {P_ambient/1e5:.3f} Bar\n"
            summary += "  Flow characteristic:\n"
            summary += "    - Oblique shocks at end of nozzle\n"
        elif self.shock_type is None:
            summary += "NO INTERNAL SHOCK:\n"
            summary += f"  Flow is UNDEREXPANDED\n"
            summary += f"  Exit pressure ≈ ambient\n"
            summary += f"  Isentropic design achieved\n"
        
        return summary
    
    def _plot_nozzle_contour(self, ax):
        """
        Plots the nozzle geometry contour with Mach number colored overlay.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes object to plot on
        """
        # Plot nozzle walls (upper and lower)
        ax.fill_between(self.x, -self.r, self.r, alpha=0.15, color='gray', label='Nozzle Geometry')
        ax.plot(self.x, self.r, 'k-', linewidth=2, label='Nozzle Wall')
        ax.plot(self.x, -self.r, 'k-', linewidth=2)
        
        # Color code the Mach number along the centerline
        # Normalize Mach for color mapping
        if self.shock_type == 'normal' and self.M_post_shock is not None:
            # Plot Mach distribution with shock
            M_to_plot = self.M_post_shock
            label_str = 'Mach (with shock)'
        else:
            M_to_plot = self.M
            label_str = 'Mach (isentropic)'
        
        # Create a colormap for Mach numbers
        M_min = np.min(M_to_plot)
        M_max = np.max(M_to_plot)
        
        # Plot line segments colored by Mach number
        for i in range(len(self.x) - 1):
            M_avg = (M_to_plot[i] + M_to_plot[i+1]) / 2
            # Normalize to [0, 1]
            M_norm = (M_avg - M_min) / (M_max - M_min) if M_max > M_min else 0.5
            
            # Use a colormap (blue=subsonic, red=supersonic)
            if M_avg < 1.0:
                color = plt.cm.Blues(0.3 + 0.7 * M_norm)
            else:
                color = plt.cm.Reds(0.3 + 0.7 * M_norm)
            
            ax.plot(self.x[i:i+2], [0, 0], color=color, linewidth=4, solid_capstyle='round')
        
        # Add shock location marker
        if self.shock_type == 'normal' and self.shock_location is not None:
            ax.axvline(self.x[self.shock_location], color='orange', linestyle='--', linewidth=2.5, alpha=0.7)
            ax.text(self.x[self.shock_location], max(self.r) * 0.9, f'Shock\nx={self.x[self.shock_location]:.3f}', 
                   ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # Add throat marker
        ax.axvline(self.x[self.throat_idx], color='green', linestyle='--', linewidth=2, alpha=0.5)
        ax.text(self.x[self.throat_idx], -max(self.r) * 0.9, f'Throat\nx={self.x[self.throat_idx]:.3f}', 
               ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        # Formatting
        ax.set_xlabel('Axial Position x (m)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Radius r (m)', fontsize=11, fontweight='bold')
        ax.set_title('Nozzle Geometry with Mach Number Distribution', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')
        ax.legend(loc='upper left', fontsize=10)
        
        # Add colorbar for Mach reference
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlBu_r, norm=plt.Normalize(vmin=M_min, vmax=M_max))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, shrink=0.8)
        cbar.set_label('Mach Number', fontsize=10, fontweight='bold')