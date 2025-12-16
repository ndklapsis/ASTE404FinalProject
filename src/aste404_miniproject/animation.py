import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from .nozzle import NozzleAnalyzer

class NozzleAnimator:
    def __init__(self, inputs, geometry):
        self.inputs = inputs
        self.geometry = geometry
        
        # Simulation Settings: 0km to 30km
        self.altitudes = np.linspace(0, 10000, 150) 
        self.frames = []

    def _get_ambient_pressure(self, altitude_m):
        """
        Standard Atmosphere Model (US Standard Atmosphere 1976).
        Returns pressure in Pa at a given altitude in meters.
        Accurate up to 86 km.
        """
        # Convert altitude to kilometers
        h_km = altitude_m / 1000.0
        
        if h_km <= 11.0:
            # Troposphere (0-11 km)
            T0 = 288.15  # Temperature at sea level (K)
            L = -0.0065  # Lapse rate (K/m)
            P0 = 101325.0  # Pressure at sea level (Pa)
            g = 9.80665  # Gravitational acceleration (m/s^2)
            M = 0.0289644  # Molar mass of air (kg/mol)
            R = 8.31432  # Universal gas constant (J/(mol*K))
            
            T = T0 + L * altitude_m
            exponent = (-g * M * altitude_m) / (R * T0 * L)
            P = P0 * (T / T0) ** exponent
            
        elif h_km <= 20.0:
            # Stratosphere Part 1 (11-20 km)
            P_11 = 22632.04  # Pressure at 11 km boundary (Pa)
            T_11 = 216.65  # Temperature at 11 km boundary (K)
            h_11 = 11000.0  # Altitude at boundary (m)
            g = 9.80665
            M = 0.0289644
            R = 8.31432
            
            exponent = (-g * M * (altitude_m - h_11)) / (R * T_11)
            P = P_11 * np.exp(exponent)
            
        elif h_km <= 32.0:
            # Stratosphere Part 2 (20-32 km)
            P_20 = 5474.89  # Pressure at 20 km boundary (Pa)
            T_20 = 216.65  # Temperature at 20 km boundary (K)
            L = 0.001  # Lapse rate (K/m)
            h_20 = 20000.0  # Altitude at boundary (m)
            g = 9.80665
            M = 0.0289644
            R = 8.31432
            
            T = T_20 + L * (altitude_m - h_20)
            exponent = (-g * M * (altitude_m - h_20)) / (R * T_20 * L)
            P = P_20 * (T / T_20) ** exponent
            
        else:
            # Above 32 km - use simplified model
            P_32 = 868.02  # Pressure at 32 km (Pa)
            T_32 = 228.65  # Temperature at 32 km (K)
            h_32 = 32000.0
            g = 9.80665
            M = 0.0289644
            R = 8.31432
            
            exponent = (-g * M * (altitude_m - h_32)) / (R * T_32)
            P = P_32 * np.exp(exponent)
        
        return P

    def precalculate(self):
        """
        Runs the numerical solver for every altitude step BEFORE plotting.
        This ensures the animation runs smoothly without lag.
        Uses standard atmosphere back pressure at each altitude.
        """
        print(f"Pre-calculating {len(self.altitudes)} flight frames with standard atmosphere...")
        
        for i, alt in enumerate(self.altitudes):
            try:
                # 1. Update Ambient Pressure using Standard Atmosphere
                current_amb = self._get_ambient_pressure(alt) * 10 #10x atmosphere to show clearer effects
                
                # 2. Create a fresh analyzer instance with updated ambient pressure
                updated_inputs = self.inputs.copy()
                updated_inputs['Pb1'] = current_amb
                
                analyzer = NozzleAnalyzer(updated_inputs, self.geometry)
                
                # 3. Solve Base Flow (Isentropic)
                analyzer.solve_isentropic()
                
                # 4. Detect and Solve Shocks
                shock_type = analyzer.detect_shock_type()
                
                # 5. Calculate normal shock if needed
                if shock_type == 'normal' and analyzer.shock_location is not None:
                    analyzer._calculate_normal_shock_flow(analyzer.shock_location)
                
                # 6. Extract Data for Plotting
                frame_data = {
                    'alt': alt,
                    'P_amb': current_amb,
                    'x': analyzer.x,
                    'M': analyzer.M,
                    'shock_x': None,
                    'shock_type': shock_type,
                    'M_exit': analyzer.M[-1],
                    'P_exit': analyzer.P[-1],
                    'M1': None,
                    'M2': None
                }
                
                # Use appropriate pressure array based on shock type
                if shock_type == 'normal' and analyzer.P_post_shock is not None:
                    frame_data['P'] = analyzer.P_post_shock
                    frame_data['P_exit'] = analyzer.P_post_shock[-1]
                    if analyzer.shock_location is not None:
                        frame_data['shock_x'] = analyzer.x[analyzer.shock_location]
                        frame_data['M1'] = analyzer.M[analyzer.shock_location]
                        frame_data['M2'] = analyzer.M_post_shock[analyzer.shock_location]
                else:
                    # Isentropic (underexpanded or oblique)
                    frame_data['P'] = analyzer.P
                
                self.frames.append(frame_data)
                
                # Progress bar
                if (i + 1) % 20 == 0:
                    print(f"  > Processed {alt/1000:.1f} km... (P_amb = {current_amb/1e5:.4f} Bar)")
                    
            except Exception as e:
                print(f"  ! Error at altitude {alt/1000:.1f} km: {str(e)}")
                continue

        print(f"Calculation Complete. Generated {len(self.frames)} frames.")

    def run(self):
        """Sets up and plays the Matplotlib animation showing nozzle evolution during ascent."""
        if not self.frames:
            self.precalculate()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10), gridspec_kw={'height_ratios': [1, 1]})
        
        # Add spacing between subplots
        plt.subplots_adjust(hspace=0.35)
        
        # Get geometry limits - handle both DataFrame and dictionary access
        x_values = self.geometry['x'].values if hasattr(self.geometry['x'], 'values') else self.geometry['x']
        x_min = float(np.min(x_values))
        x_max = float(np.max(x_values))
        
        # Top plot: Pressure distribution
        ax1.set_xlim(x_min, x_max)
        ax1.set_ylim(0, self.inputs['Pc'] / 1e5 * 1.2)
        ax1.set_ylabel('Pressure (Bar)', fontsize=11, fontweight='bold')
        ax1.set_title('Nozzle Pressure Distribution During Ascent', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Bottom plot: Mach number distribution
        ax2.set_xlim(x_min, x_max)
        ax2.set_ylim(0, 4.0)
        ax2.set_xlabel('Nozzle Axial Position (m)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Mach Number', fontsize=11, fontweight='bold')
        ax2.axhline(1.0, color='gray', linestyle='--', alpha=0.5, linewidth=1, label='Sonic (M=1)')
        ax2.grid(True, alpha=0.3)
        
        # Initialize plot objects - Pressure
        line_pressure, = ax1.plot([], [], 'b-', lw=2.5, label='Internal Pressure')
        line_ambient_p, = ax1.plot([], [], 'g--', lw=2, label='Ambient Pressure')
        shock_marker_p = ax1.axvline(0, color='r', ls='--', lw=2, alpha=0)
        
        # Initialize plot objects - Mach
        line_mach, = ax2.plot([], [], 'b-', lw=2.5, label='Mach Distribution')
        shock_marker_m = ax2.axvline(0, color='r', ls='--', lw=2, alpha=0, label='Shock Location')
        
        # Info Text (on pressure plot)
        stats_text = ax1.text(0.02, 0.97, "", transform=ax1.transAxes, 
                              fontsize=11, verticalalignment='top',
                              bbox=dict(boxstyle="round", fc="lightyellow", ec="gray", alpha=0.95))

        def init():
            line_pressure.set_data([], [])
            line_ambient_p.set_data([], [])
            shock_marker_p.set_alpha(0)
            line_mach.set_data([], [])
            shock_marker_m.set_alpha(0)
            stats_text.set_text("")
            return line_pressure, line_ambient_p, shock_marker_p, line_mach, shock_marker_m, stats_text

        def update(frame):
            # Unpack data
            x = frame['x']
            P = frame['P'] / 1e5  # Convert to Bar
            M = frame['M']
            P_amb = frame['P_amb'] / 1e5
            P_exit = frame['P_exit'] / 1e5
            M_exit = frame['M_exit']
            alt_km = frame['alt'] / 1000.0
            shock_type = frame['shock_type']
            
            # Update Pressure Curves
            line_pressure.set_data(x, P)
            line_ambient_p.set_data([x[0], x[-1]], [P_amb, P_amb])
            
            # Update Mach curve
            line_mach.set_data(x, M)
            
            # Update Shock Marker (if normal shock exists)
            if frame['shock_x'] is not None and shock_type == 'normal' and frame['M1'] is not None:
                shock_marker_p.set_xdata([frame['shock_x']])
                shock_marker_p.set_alpha(1.0)
                shock_marker_m.set_xdata([frame['shock_x']])
                shock_marker_m.set_alpha(1.0)
                
                M1 = frame['M1']
                M2 = frame['M2']
                status = f"NORMAL SHOCK: M {M1:.2f} → {M2:.3f}"
            else:
                shock_marker_p.set_alpha(0.0)
                shock_marker_m.set_alpha(0.0)
                
                # Determine flow regime
                if P_exit > P_amb:
                    status = "UNDEREXPANDED (Clean Exit)"
                elif shock_type == 'oblique':
                    status = "OVEREXPANDED (Oblique Shock)"
                else:
                    status = "OVEREXPANDED (External Shock)"

            # Update Statistics Text
            stats_text.set_text(
                f"Altitude: {alt_km:.2f} km\n"
                f"Ambient P: {P_amb:.4f} Bar\n"
                f"Exit Mach: {M_exit:.3f}\n"
                f"Exit Pressure: {P_exit:.4f} Bar\n"
                f"Status: {status}"
            )
            
            return line_pressure, line_ambient_p, shock_marker_p, line_mach, shock_marker_m, stats_text

        # Create Animation
        # interval=300 means 300ms per frame (~3.3 fps) - much slower for detailed observation
        ani = FuncAnimation(fig, update, frames=self.frames, 
                            init_func=init, blit=True, interval=300, repeat=True)
        
        fig.suptitle(f"Rocket Nozzle Flow Evolution During Ascent (Thrust: {self.inputs['NominalThrust']} N)", 
                     fontsize=14, fontweight='bold')
        
        ax1.legend(loc='upper right', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)
        
        plt.tight_layout()
        plt.show()