# Nozzle Shock Detection - Usage Guide

## Overview
The `NozzleAnalyzer` class has been enhanced to detect and analyze normal shocks, oblique shocks, and expansion fans in nozzle flows. It automatically determines the flow regime and plots the results.

## New Features

### 1. Shock Detection (`detect_shock_type()`)
Compares the isentropic exit pressure with ambient pressure to determine flow regime:

- **UNDEREXPANDED**: Exit pressure ≥ ambient pressure (no internal shocks)
- **OVEREXPANDED with NORMAL SHOCK**: Exit pressure < ambient, internal shock found
- **OVEREXPANDED with OBLIQUE SHOCKS**: Exit pressure < ambient, no internal shock (external shock system)

### 2. Normal Shock Analysis (`_calculate_normal_shock_flow()`)
When a normal shock is detected:
- Finds the shock location that produces exit pressure close to ambient
- Calculates pre-shock (supersonic) and post-shock (subsonic) conditions
- Accounts for stagnation pressure loss across the shock
- Solves for subsonic flow downstream of the shock

### 3. Enhanced Plotting (`plot_results()`)
Now displays:
- **Mach distribution** (isentropic + with shock overlay)
- **Pressure distribution** (isentropic + with shock overlay + ambient reference line)
- **Temperature distribution** (isentropic + with shock overlay)
- **Summary table** showing shock analysis results

## Usage Example

```python
from aste404_miniproject.nozzle import NozzleAnalyzer
import pandas as pd

# Load input data
inputs = {
    'Pc': 3.5e6,        # Chamber pressure (Pa)
    'Tc': 3000,         # Chamber temperature (K)
    'gamma': 1.25,      # Specific heat ratio
    'Pb1': 101325       # Ambient pressure (Pa)
}

# Load geometry
geometry = pd.read_csv('geometry.csv')

# Create analyzer
analyzer = NozzleAnalyzer(inputs, geometry)

# Solve isentropic flow
analyzer.solve_isentropic()

# Detect shock type and calculate post-shock flow (if applicable)
shock_type = analyzer.detect_shock_type()
print(f"Detected shock type: {shock_type}")

# Plot results with shock overlays
analyzer.plot_results()
```

## Shock Type Detection Logic

```
Exit Pressure vs Ambient
├─ Pe ≥ 0.98 * Pa  → UNDEREXPANDED (no shock)
└─ Pe < 0.98 * Pa  → OVEREXPANDED
   ├─ Find normal shock location that matches Pa at exit
   ├─ If found (error < 5%) → NORMAL SHOCK
   └─ If not found → OBLIQUE SHOCKS (external)
```

## Key Results Stored

After `detect_shock_type()`:
- `analyzer.shock_type`: 'normal', 'oblique', or None
- `analyzer.shock_location`: Index where shock occurs (normal shock only)
- `analyzer.M_post_shock`: Mach distribution with shock
- `analyzer.P_post_shock`: Pressure distribution with shock
- `analyzer.T_post_shock`: Temperature distribution with shock

## Normal Shock Methodology

1. **Pre-shock flow**: Uses isentropic relations from chamber to shock location
2. **Shock crossing**: Applies normal shock relations (M1 → M2, pressure jump)
3. **Post-shock flow**: Assumes isentropic subsonic flow with reduced stagnation pressure
4. **Effective throat**: Accounts for entropy increase via $A_t^* = A_t / P_{02}/P_{01}$

## Future Enhancements

- [ ] Oblique shock analysis with full theta-beta-M relations
- [ ] Expansion fan (Prandtl-Meyer) analysis
- [ ] Shock location refinement with finer iteration
- [ ] Entropy layer effects
- [ ] 2D/3D flow visualization
