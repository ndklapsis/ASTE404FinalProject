import numpy as np
from .gas_dynamics import standard_atmosphere, area_mach_relation

class EngineDesigner:
    def __init__(self, thrust, pc, alt, propellant, time):
        self.F, self.Pc, self.alt = thrust, pc, alt
        self.prop, self.time = propellant, time
        self.gamma = propellant['gamma']
        self.R = 8.314 / propellant['MW']
        self.Tc = propellant['Tc']

    def design(self):
        P_amb, _, _ = standard_atmosphere(self.alt)
        if P_amb >= self.Pc: raise ValueError("Chamber pressure too low for altitude.")

        # 1. Optimal Expansion (Pe = Pa)
        term = (self.Pc / P_amb) ** ((self.gamma - 1) / self.gamma)
        Me = np.sqrt((2 / (self.gamma - 1)) * (term - 1))
        
        # 2. Geometry
        Te = self.Tc / (1 + 0.5 * (self.gamma - 1) * Me**2)
        Ve = Me * np.sqrt(self.gamma * self.R * Te)
        m_dot = self.F / Ve
        
        gam_term = np.sqrt(self.gamma) * (2/(self.gamma+1))**((self.gamma+1)/(2*(self.gamma-1)))
        A_star = (m_dot * np.sqrt(self.R * self.Tc)) / (self.Pc * gam_term)
        epsilon = area_mach_relation(Me, self.gamma)
        
        # 3. Propellants
        m_total = m_dot * self.time
        of = self.prop['OF']
        m_ox = m_total * (of/(1+of))
        m_fu = m_total / (1+of)
        
        print("\n" + "="*40)
        print("   ENGINE DESIGN REPORT")
        print("="*40)
        print(f"Inputs: {self.F/1000}kN Thrust @ {self.alt}km, {self.prop['name']}")
        print("-" * 40)
        print(f"Throat Radius:   {np.sqrt(A_star/np.pi)*1000:.2f} mm")
        print(f"Exit Radius:     {np.sqrt(A_star*epsilon/np.pi)*1000:.2f} mm")
        print(f"Expansion Ratio: {epsilon:.2f}")
        print(f"Isp (Ideal):     {Ve/9.81:.1f} s")
        print("-" * 40)
        print(f"Propellants ({self.time}s burn):")
        print(f"Oxidizer:        {m_ox:.1f} kg")
        print(f"Fuel:            {m_fu:.1f} kg")
        print("="*40 + "\n")