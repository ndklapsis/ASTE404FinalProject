PROPELLANT_DATA = {
    "methalox": {"name": "LCH4 / LOX", "gamma": 1.18, "Tc": 3500.0, "MW": 20.0e-3, "OF": 3.4, "rho_ox": 1141, "rho_f": 422},
    "hydrolox": {"name": "LH2 / LOX", "gamma": 1.22, "Tc": 3300.0, "MW": 13.0e-3, "OF": 5.5, "rho_ox": 1141, "rho_f": 71},
    "kerolox":  {"name": "RP-1 / LOX", "gamma": 1.24, "Tc": 3600.0, "MW": 24.0e-3, "OF": 2.3, "rho_ox": 1141, "rho_f": 810},
    "cold_gas": {"name": "N2 Cold Gas", "gamma": 1.4,  "Tc": 300.0,  "MW": 28.0e-3, "OF": 0.0, "rho_ox": 0,    "rho_f": 800} # Dummy for cold tests
}

def get_propellant(name_or_vals: str) -> dict:
    """
    Accepts preset name 'methalox' OR string 'gamma,Tc,MW,OF'.
    """
    if "," in name_or_vals:
        # User provided custom values
        try:
            parts = [float(x) for x in name_or_vals.split(',')]
            return {
                "name": "Custom Mix",
                "gamma": parts[0],
                "Tc": parts[1],
                "MW": parts[2],
                "OF": parts[3] if len(parts) > 3 else 0,
                "rho_ox": 1000, "rho_f": 1000 # Defaults for sizing
            }
        except:
            raise ValueError("Custom format must be: 'gamma,Tc,MW,OF'")
            
    key = name_or_vals.lower().strip()
    if key in PROPELLANT_DATA:
        return PROPELLANT_DATA[key]
    raise ValueError(f"Unknown propellant. Choose from {list(PROPELLANT_DATA.keys())} or provide CSV string.")