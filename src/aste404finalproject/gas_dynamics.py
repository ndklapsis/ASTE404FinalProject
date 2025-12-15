import numpy as np

def area_mach_relation(M: float, gamma: float) -> float:
    """Calculates A/A* given Mach number and gamma."""
    if M <= 0: return float('inf')
    term1 = 1.0 / M
    term2 = (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * M**2)
    exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))
    return term1 * (term2 ** exponent)

def area_mach_derivative(M: float, gamma: float) -> float:
    """Derivative d(A/A*)/dM for Newton-Raphson solver."""
    if M <= 1e-6: return -1e6
    A_ratio = area_mach_relation(M, gamma)
    term1 = (M**2 - 1.0)
    term2 = M * (1.0 + 0.5 * (gamma - 1.0) * M**2)
    return A_ratio * (term1 / term2)

def normal_shock_relations(M1: float, gamma: float) -> dict:
    """
    Calculates properties across a normal shock (Station 1 -> Station 2).
    """
    # Mach after shock
    num = 1.0 + 0.5 * (gamma - 1.0) * M1**2
    den = gamma * M1**2 - 0.5 * (gamma - 1.0)
    M2 = np.sqrt(num / den)
    
    # Static Pressure Ratio (P2/P1)
    p_ratio = 1.0 + (2.0 * gamma / (gamma + 1.0)) * (M1**2 - 1.0)
    
    # Stagnation Pressure Ratio (P02/P01) - Represents Entropy Loss
    term1_num = (gamma + 1) * M1**2
    term1_den = (gamma - 1) * M1**2 + 2
    term2_num = gamma + 1
    term2_den = 2 * gamma * M1**2 - (gamma - 1)
    
    p0_ratio = ( (term1_num/term1_den)**(gamma/(gamma-1)) ) * \
               ( (term2_num/term2_den)**(1/(gamma-1)) )
               
    return {"M2": M2, "P2_P1": p_ratio, "P02_P01": p0_ratio}

def standard_atmosphere(alt_km: float) -> tuple:
    """Returns P [Pa], T [K], rho [kg/m^3] for given altitude."""
    # Simple troposphere/stratosphere model for project purposes
    if alt_km > 47: 
        # Fallback for very high altitude (vacuum approximation)
        return 1.0, 270.0, 1e-9
        
    # Standard layers
    htab = [0.0, 11.0, 20.0, 32.0, 47.0]
    ptab = [101325.0, 22632.1, 5474.89, 868.019, 110.906]
    ttab = [288.15, 216.65, 216.65, 228.65, 270.65]
    ltab = [-6.5, 0.0, 1.0, 2.8, 0.0]

    i = 0
    for j in range(len(htab)-1):
        if htab[j] <= alt_km < htab[j+1]:
            i = j; break
            
    base_h, base_t, base_p, lapse = htab[i], ttab[i], ptab[i], ltab[i]
    
    if lapse == 0:
        T = base_t
        P = base_p * np.exp(-9.81 * 1000 * (alt_km - base_h) / (287.0 * T))
    else:
        T = base_t + lapse * (alt_km - base_h)
        P = base_p * (base_t / T) ** (9.81 * 1000 / (287.0 * lapse))
        
    return P, T, P/(287.0*T)