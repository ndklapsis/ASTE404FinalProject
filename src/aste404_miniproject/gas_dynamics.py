import numpy as np
import numbers
from .solver import HybridSolver

# --- 1. IDEAL ROCKET FLOW ---

def c_star(gamma, r, t0):
    """
    Calculates the characteristic velocity (c*) for an ideal rocket.

    Parameters
    ----------
    gamma : float or numpy.ndarray
        Ratio of specific heats (unitless).
    r : float or numpy.ndarray
        Specific gas constant (J/ (kg * K))
    t0 : float or numpy.ndarray
        Stagnation temperature  (K)

    Returns
    -------
    float or numpy.ndarray
        Characteristic velocity (c*) in units of velocity 
        (matching the units of sqrt(r * t0))

    Raises
    ------
    TypeError
        If any input is not numeric
    ValueError
        If inputs are outside their valid physical domains:
        - gamma <= 1
        - r <= 0
        - t0 <= 0
    
    Notes
    -----
    c* = sqrt( (1/gamma) * ( (gamma+1)/2 )^((gamma+1)/(gamma-1)) * R * T0 )
    
 
    """
    # --- Input Validation ---
    for arg_name, arg_val in [('gamma', gamma), ('r', r), ('t0', t0)]:
        if not isinstance(arg_val, (numbers.Number, np.ndarray)):
            raise TypeError(f"Input '{arg_name}' must be numeric (float or numpy array).")

    # Convert scalars to 0-d arrays to make agnostic validation
    gamma = np.asarray(gamma)
    r = np.asarray(r)
    t0 = np.asarray(t0)

    if np.any(gamma <= 1):
        raise ValueError("Ratio of specific heats (gamma) must be > 1.")
    if np.any(r <= 0):
        raise ValueError("Specific gas constant (r) must be > 0.")
    if np.any(t0 <= 0):
        raise ValueError("Stagnation temperature (t0) must be > 0 (absolute).")

    # --- Equation ---
    g = gamma
    term1 = 1 / g
    term2 = ((g + 1) / 2) ** ((g + 1) / (g - 1))
    term3 = r * t0
    
    c_star = np.sqrt(term1 * term2 * term3)
    
    return c_star

def c_f(gamma, pe_p0, pa_p0, ae_at):
    """
    Calculates the thrust coefficient (CF) for an ideal rocket.

    Parameters
    ----------
    gamma : float or numpy.ndarray
        Ratio of specific heats (unitless)
    pe_p0 : float or numpy.ndarray
        Nozzle exit pressure to stagnation pressure ratio (unitless)
    pa_p0 : float or numpy.ndarray
        Ambient pressure to stagnation pressure ratio (unitless)
    ae_at : float or numpy.ndarray
        Nozzle exit area to throat area ratio (unitless)

    Returns
    -------
    float or numpy.ndarray
        Thrust coefficient (CF) (unitless)

    Raises
    ------
    TypeError
        If any input is not numeric.
    ValueError
        If inputs are outside their valid physical domains:
        - gamma <= 1
        - pe_p0 not in [0, 1)
        - pa_p0 not in [0, 1)
        - ae_at < 1

    Notes
    -----
    CF = sqrt( (2*g^2)/(g-1) * (2/(g+1))^((g+1)/(g-1)) * (1 - (pe_p0)^((g-1)/g)) ) 
         + (pe_p0 - pa_p0) * ae_at

    """
    # --- Input Validation [cite: 101, 102] ---
    for arg_name, arg_val in [('gamma', gamma), ('pe_p0', pe_p0), ('pa_p0', pa_p0), ('ae_at', ae_at)]:
        if not isinstance(arg_val, (numbers.Number, np.ndarray)):
            raise TypeError(f"Input '{arg_name}' must be numeric (float or numpy array).")

    # Convert scalars to 0-d arrays to allow universal validation
    gamma = np.asarray(gamma)
    pe_p0 = np.asarray(pe_p0)
    pa_p0 = np.asarray(pa_p0)
    ae_at = np.asarray(ae_at)

    if np.any(gamma <= 1):
        raise ValueError("Ratio of specific heats (gamma) must be > 1.")
    if np.any((pe_p0 < 0) | (pe_p0 >= 1)):
        raise ValueError("Pressure ratio (pe_p0) must be in the range [0, 1).")
    if np.any((pa_p0 < 0) | (pa_p0 >= 1)):
        raise ValueError("Pressure ratio (pa_p0) must be in the range [0, 1).")
    if np.any(ae_at < 1):
        raise ValueError("Nozzle area ratio (ae_at) must be >= 1.")

    # --- Equation ---
    g = gamma 

    # momentum thrust
    term1 = (2 * g**2) / (g - 1)
    term2 = (2 / (g + 1)) ** ((g + 1) / (g - 1))
    term3 = 1 - (pe_p0) ** ((g - 1) / g)
    momentum_thrust = np.sqrt(term1 * term2 * term3)

    # pressure contribution
    pressure_thrust = (pe_p0 - pa_p0) * ae_at
    
    c_f = momentum_thrust + pressure_thrust
    
    return c_f

# --- 2. ISENTROPIC FLOW ---

def area_mach_relation(M: float, gamma: float) -> float:
    """Calculates A/A*
    
    Parameters
    ----------
    M : float
        Mach number (unitless)
    gamma : float
        Ratio of specific heats (unitless)

    Returns
    -------
    float
        Area ratio A/A* (unitless)

    Notes
    -----
    A/A* = (1/M) * [ (2/(gamma+1)) * (1 + (gamma-1)/2 * M^2) ]^((gamma+1)/(2*(gamma-1)))

    if M <= 0, returns infinity.
    """
    if M <= 0: return float('inf')
    term1 = 1.0 / M
    term2 = (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * M**2)
    exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))
    return term1 * (term2 ** exponent)

def area_mach_derivative(M: float, gamma: float) -> float:
    """Derivative d(A/A*)/dM (For Newton Solver).
    
    Parameters
    ----------
    M : float
        Mach number (unitless)
    gamma : float
        Ratio of specific heats (unitless)

    Returns
    -------
    float
        Derivative d(A/A*)/dM (unitless)

    Notes
    -----
    d(A/A*)/dM = A/A* * (M^2 - 1) / (M * (1 + 0.5*(gamma-1)*M^2))

    Used primarily for newton raphson solver.
    """
    if M <= 1e-6: return -1e6
    A_ratio = area_mach_relation(M, gamma)
    term1 = (M**2 - 1.0)
    term2 = M * (1.0 + 0.5 * (gamma - 1.0) * M**2)
    return A_ratio * (term1 / term2)

def solve_area_mach(A_Astar: float, gamma: float, supersonic: bool = True) -> float:
    """
    Solves for Mach number given area ratio A/A*.

    Parameters
    ----------
    A_Astar : float
        Area ratio A/A* (unitless)
    gamma : float
        Ratio of specific heats (unitless)
    supersonic : bool, optional
        If True, solves for supersonic Mach. If False, subsonic. Default is True.

    Returns
    -------
    float
        Mach number (unitless)
    """
    solver = HybridSolver()
    
    # Solve: A/A*(M) - target = 0
    func = lambda m: area_mach_relation(m, gamma) - A_Astar
    deriv = lambda m: area_mach_derivative(m, gamma)
    
    if supersonic:
        return solver.solve(func, deriv, guess=2.0, low=1.0, high=50.0)
    else:
        return solver.solve(func, deriv, guess=0.2, low=1e-6, high=1.0)
    
def isentropic_P_P0(M: float, gamma: float) -> float:
    """
    Calculates static to stagnation pressure ratio P/P0 for isentropic flow.

    Parameters
    ----------
    M : float
        Mach number (unitless)
    gamma : float
        Ratio of specific heats (unitless)

    Returns
    -------
    float
        Pressure ratio P/P0 (unitless)

    Notes
    -----
    P/P0 = (1 + 0.5 * (gamma - 1) * M^2) ^ (-gamma / (gamma - 1))
    """
    return (1 + 0.5 * (gamma - 1) * M**2) ** (-gamma / (gamma - 1))

def isentropic_T_T0(M: float, gamma: float) -> float:
    """
    Calculates static to stagnation temperature ratio T/T0 for isentropic flow.

    Parameters
    ----------
    M : float
        Mach number (unitless)
    gamma : float
        Ratio of specific heats (unitless)

    Returns
    -------
    float
        Temperature ratio T/T0 (unitless)
        
    Notes
    -----
    T/T0 = (1 + 0.5 * (gamma - 1) * M^2) ^ -1
    """

    return (1 + 0.5 * (gamma - 1) * M**2) ** -1

# --- 3. NORMAL SHOCK ---

def normal_shock_relations(M1: float, gamma: float) -> dict:
    """
    Calculates the mach number, pressure ratio, and stagnation pressure ratio immediately after a normal shock.

    Parameters
    ----------
    M1 : float
        Incoming Mach number before the shock.
    gamma : float
        Ratio of specific heats (unitless).

    Returns
    -------
    dict
        Dictionary with keys:
        - "M2": Mach number after the shock
        - "P2_P1": Static pressure ratio across the shock (P2/P1)
        - "P02_P01": Stagnation pressure ratio across the shock (P02/P01)

    Notes
    -----
    If M1 <= 1, the function returns M2 = M1, P2/P1 = 1.0, P02/P01 = 1.0 (no shock).
    """
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

# --- 4. PRANDTL-MEYER EXPANSION ---

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

# --- 5. OBLIQUE SHOCK (Theta-Beta-M) ---

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