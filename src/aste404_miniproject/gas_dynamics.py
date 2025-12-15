import numpy as np
from .solver import HybridSolver

# --- 1. ISENTROPIC FLOW ---
def area_mach_relation(M: float, gamma: float) -> float:
    """Calculates A/A*."""
    if M <= 0: return float('inf')
    term1 = 1.0 / M
    term2 = (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * M**2)
    exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))
    return term1 * (term2 ** exponent)

def area_mach_derivative(M: float, gamma: float) -> float:
    """Derivative d(A/A*)/dM (For Newton Solver)."""
    if M <= 1e-6: return -1e6
    A_ratio = area_mach_relation(M, gamma)
    term1 = (M**2 - 1.0)
    term2 = M * (1.0 + 0.5 * (gamma - 1.0) * M**2)
    return A_ratio * (term1 / term2)

def isentropic_P_P0(M: float, gamma: float) -> float:
    return (1 + 0.5 * (gamma - 1) * M**2) ** (-gamma / (gamma - 1))

def isentropic_T_T0(M: float, gamma: float) -> float:
    return (1 + 0.5 * (gamma - 1) * M**2) ** -1

# --- 2. NORMAL SHOCK ---

def normal_shock_relations(M1: float, gamma: float) -> dict:
    """Returns M2, P2/P1, P02/P01."""
    if M1 <= 1: return {"M2": M1, "P2_P1": 1.0, "P02_P01": 1.0}
    
    # M2 Relation
    num = 1.0 + 0.5 * (gamma - 1.0) * M1**2
    den = gamma * M1**2 - 0.5 * (gamma - 1.0)
    M2 = np.sqrt(num / den)
    
    # Static Pressure Ratio P2/P1
    p_ratio = 1.0 + (2.0 * gamma / (gamma + 1.0)) * (M1**2 - 1.0)
    
    # Stagnation Pressure Ratio P02/P01
    term1_num = (gamma + 1) * M1**2
    term1_den = (gamma - 1) * M1**2 + 2
    term2_num = gamma + 1
    term2_den = 2 * gamma * M1**2 - (gamma - 1)
    p0_ratio = ( (term1_num/term1_den)**(gamma/(gamma-1)) ) * \
               ( (term2_num/term2_den)**(1/(gamma-1)) )
               
    return {"M2": M2, "P2_P1": p_ratio, "P02_P01": p0_ratio}

# --- 3. PRANDTL-MEYER EXPANSION ---

def prandtl_meyer_function(M: float, gamma: float) -> float:
    """Returns the Prandtl-Meyer angle (nu) in DEGREES."""
    if M < 1.0: return 0.0
    term1 = np.sqrt((gamma + 1) / (gamma - 1))
    term2 = np.arctan(np.sqrt((gamma - 1) / (gamma + 1) * (M**2 - 1)))
    term3 = np.arctan(np.sqrt(M**2 - 1))
    nu_rad = term1 * term2 - term3
    return np.degrees(nu_rad)

def prandtl_meyer_derivative(M: float, gamma: float) -> float:
    """Derivative d(nu)/dM used for solving inverse expansion."""
    if M <= 1.0: return 0.0
    M2_minus_1 = M**2 - 1
    if M2_minus_1 <= 0: return 0.0
    
    # Analytical derivative of PM function
    term = (np.sqrt(M2_minus_1)) / (1 + 0.5*(gamma-1)*M**2) / M
    # Convert to degrees because our target is degrees
    return np.degrees(term)

def solve_expansion_fan(M1: float, theta_deg: float, gamma: float) -> float:
    """
    Finds M2 after turning corner by theta degrees.
    Relation: nu(M2) = nu(M1) + theta
    """
    nu_M1 = prandtl_meyer_function(M1, gamma)
    target_nu = nu_M1 + theta_deg
    
    solver = HybridSolver()
    
    # Solve: PM(M) - target = 0
    func = lambda m: prandtl_meyer_function(m, gamma) - target_nu
    deriv = lambda m: prandtl_meyer_derivative(m, gamma)
    
    # Guess M2 > M1. Upper bound arbitrary high Mach (20).
    return solver.solve(func, deriv, guess=M1+1.0, low=M1, high=20.0)

# --- 4. OBLIQUE SHOCK (Theta-Beta-M) ---

def theta_beta_mach(M1: float, beta_deg: float, gamma: float) -> float:
    """Calculates deflection angle theta given shock angle beta."""
    beta = np.radians(beta_deg)
    num = M1**2 * np.sin(beta)**2 - 1
    den = M1**2 * (gamma + np.cos(2*beta)) + 2
    tan_theta = 2 * (1 / np.tan(beta)) * (num / den)
    return np.degrees(np.arctan(tan_theta))

def solve_oblique_beta(M1: float, theta_deg: float, gamma: float) -> float:
    """
    Solves for the weak shock wave angle Beta given deflection Theta.
    """
    solver = HybridSolver()
    
    # Solve: Calculated_Theta(Beta) - Target_Theta = 0
    func = lambda b: theta_beta_mach(M1, b, gamma) - theta_deg
    
    # Simple finite difference derivative since the analytical one is messy
    def deriv(b):
        h = 1e-5
        return (func(b+h) - func(b)) / h
    
    # Weak shock is usually between asin(1/M) and 90 degrees.
    mu = np.degrees(np.arcsin(1/M1))
    return solver.solve(func, deriv, guess=mu+5, low=mu, high=90.0)