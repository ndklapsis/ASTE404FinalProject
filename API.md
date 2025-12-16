# API Documentation

## Complete Reference for ASTE 404 Nozzle Simulation Toolbox

---

## Table of Contents

1. [Gas Dynamics Module](#gas-dynamics-module)
2. [NozzleAnalyzer Class](#nozzleanalyzer-class)
3. [NozzleAnimator Class](#nozzleanimator-class)
4. [HybridSolver Class](#hybridsolver-class)
5. [Utility Functions](#utility-functions)

---

**Version Note:** This documentation covers v0.3.0. Modules `design.py` and `propellants.py` are not yet functional and will be available in v0.4.

---

## Gas Dynamics Module

Location: `aste404_miniproject.gas_dynamics`

Complete set of compressible flow functions for rocket propulsion analysis.

### Ideal Rocket Functions

#### `c_star(gamma, r, t0)`

Calculates the characteristic velocity (c*) for an ideal rocket engine.

**Parameters:**
- `gamma` (float or ndarray): Ratio of specific heats γ = Cp/Cv (unitless)
- `r` (float or ndarray): Specific gas constant (J/(kg·K))
- `t0` (float or ndarray): Stagnation (chamber) temperature (K)

**Returns:**
- `float or ndarray`: Characteristic velocity (m/s)

**Formula:**
$$c^* = \sqrt{\frac{1}{\gamma} \left(\frac{\gamma+1}{2}\right)^{\frac{\gamma+1}{\gamma-1}} RT_0}$$

**Example:**
```python
from aste404_miniproject import c_star

c_star_val = c_star(gamma=1.2, r=287, t0=2800)
# Returns: ~1850 m/s
```

#### `c_f(gamma, pe_p0, pa_p0, ae_at)`

Calculates the thrust coefficient (CF) accounting for exit pressure conditions.

**Parameters:**
- `gamma` (float or ndarray): Ratio of specific heats (unitless)
- `pe_p0` (float or ndarray): Exit pressure ratio P_e/P_0 (unitless, 0 < value < 1)
- `pa_p0` (float or ndarray): Ambient pressure ratio P_a/P_0 (unitless, 0 < value < 1)
- `ae_at` (float or ndarray): Area ratio A_e/A_t (unitless, ≥ 1)

**Returns:**
- `float or ndarray`: Thrust coefficient (unitless, typically 0.6-1.8)

**Notes:**
- Accounts for pressure term: (Pe - Pa) × Ae/At
- Momentum term: ∫∫ ρu² dA / (Pc × At)

**Example:**
```python
from aste404_miniproject import c_f

cf = c_f(gamma=1.4, pe_p0=0.1, pa_p0=0.01, ae_at=5.0)
```

---

### Isentropic Flow Functions

#### `area_mach_relation(M, gamma)`

Calculates the normalized nozzle area as a function of Mach number.

**Parameters:**
- `M` (float or ndarray): Mach number (unitless)
- `gamma` (float or ndarray): Ratio of specific heats (unitless)

**Returns:**
- `float or ndarray`: Normalized area ratio A/A* (unitless)

**Formula:**
$$\frac{A}{A^*} = \frac{1}{M}\left[\frac{2}{\gamma+1}\left(1 + \frac{\gamma-1}{2}M^2\right)\right]^{\frac{\gamma+1}{2(\gamma-1)}}$$

**Notes:**
- Minimum at M=1 (throat), value = 1.0
- Subsonic (M<1): A/A* decreases with decreasing M
- Supersonic (M>1): A/A* increases with increasing M

**Example:**
```python
from aste404_miniproject import area_mach_relation

# Find area ratio at M=2.5
area_ratio = area_mach_relation(2.5, 1.4)
# Returns: ~1.638
```

#### `area_mach_derivative(M, gamma)`

Calculates the derivative of area-Mach relation (used by solver).

**Parameters:**
- `M` (float or ndarray): Mach number
- `gamma` (float or ndarray): Ratio of specific heats

**Returns:**
- `float or ndarray`: d(A/A*)/dM

**Usage:** Used internally by HybridSolver for Newton-Raphson iterations.

#### `isentropic_P_P0(M, gamma)`

Pressure ratio for isentropic flow.

**Parameters:**
- `M` (float or ndarray): Mach number
- `gamma` (float or ndarray): Ratio of specific heats

**Returns:**
- `float or ndarray`: P/P0 (unitless, 0 < value ≤ 1)

**Formula:**
$$\frac{P}{P_0} = \left(1 + \frac{\gamma-1}{2}M^2\right)^{-\gamma/(\gamma-1)}$$

**Example:**
```python
from aste404_miniproject import isentropic_P_P0

# Pressure at exit Mach 2.5
p_ratio = isentropic_P_P0(2.5, 1.4)
# Returns: ~0.0585 (5.85% of chamber pressure)
```

#### `isentropic_T_T0(M, gamma)`

Temperature ratio for isentropic flow.

**Parameters:**
- `M` (float or ndarray): Mach number
- `gamma` (float or ndarray): Ratio of specific heats

**Returns:**
- `float or ndarray`: T/T0 (unitless, 0 < value ≤ 1)

**Formula:**
$$\frac{T}{T_0} = \left(1 + \frac{\gamma-1}{2}M^2\right)^{-1}$$

#### `isentropic_rho_rho0(M, gamma)`

Density ratio for isentropic flow.

**Parameters:**
- `M` (float or ndarray): Mach number
- `gamma` (float or ndarray): Ratio of specific heats

**Returns:**
- `float or ndarray`: ρ/ρ0 (unitless, 0 < value ≤ 1)

---

### Shock Functions

#### `normal_shock_relations(M1, gamma)`

Calculates all properties across a normal shock.

**Parameters:**
- `M1` (float or ndarray): Upstream (pre-shock) Mach number (M1 > 1)
- `gamma` (float or ndarray): Ratio of specific heats

**Returns:**
- `dict` with keys:
  - `'M2'`: Post-shock Mach number (unitless, M2 < 1)
  - `'P2_P1'`: Pressure ratio P2/P1
  - `'T2_T1'`: Temperature ratio T2/T1
  - `'rho2_rho1'`: Density ratio ρ2/ρ1
  - `'P02_P01'`: Stagnation pressure ratio (accounts for entropy rise)
  - `'T02_T01'`: Stagnation temperature ratio (typically = 1.0)

**Formulas:**
$$M_2^2 = \frac{2 + (\gamma-1)M_1^2}{2\gamma M_1^2 - (\gamma-1)}$$

$$\frac{P_2}{P_1} = 1 + \frac{2\gamma}{\gamma+1}(M_1^2 - 1)$$

$$\frac{P_{02}}{P_{01}} = \frac{(2\gamma M_1^2 - (\gamma-1))(\gamma+1)}{((\gamma+1)M_1)^2} \left(1 + \frac{\gamma-1}{2}M_1^2\right)^{-\gamma/(\gamma-1)}$$

**Example:**
```python
from aste404_miniproject import normal_shock_relations

shock = normal_shock_relations(M1=2.5, gamma=1.4)
print(f"M2 = {shock['M2']:.3f}")        # ~0.513
print(f"P2/P1 = {shock['P2_P1']:.3f}")  # ~5.675
print(f"P02/P01 = {shock['P02_P01']:.3f}")  # ~0.499
```

#### `prandtl_meyer_function(M, gamma)`

Calculates the Prandtl-Meyer function ν(M).

**Parameters:**
- `M` (float or ndarray): Mach number (M > 1)
- `gamma` (float or ndarray): Ratio of specific heats

**Returns:**
- `float or ndarray`: Prandtl-Meyer angle (degrees)

**Notes:**
- Used to analyze expansion fans
- ν increases monotonically with M for supersonic flow
- Maximum expansion angle: νmax = (π/2)(√((γ+1)/(γ-1)) - 1)

**Example:**
```python
from aste404_miniproject import prandtl_meyer_function

nu = prandtl_meyer_function(M=2.5, gamma=1.4)
# Returns: ~32.23 degrees
```

#### `solve_expansion_fan(nu1, nu2, gamma)`

Solves expansion fan flow between two Prandtl-Meyer angles.

**Parameters:**
- `nu1` (float): Initial Prandtl-Meyer angle (degrees)
- `nu2` (float): Final Prandtl-Meyer angle (degrees)
- `gamma` (float): Ratio of specific heats

**Returns:**
- `dict` with calculated Mach and pressure conditions

**Usage:** For analyzing isentropic expansion fans (e.g., overexpanded nozzles).

#### `solve_oblique_beta(M1, theta, gamma)`

Solves oblique shock angle using θ-β-M relation.

**Parameters:**
- `M1` (float): Upstream Mach number
- `theta` (float): Flow deflection angle (degrees)
- `gamma` (float): Ratio of specific heats

**Returns:**
- `float or dict`: Shock angle β (degrees) or solution structure

**Notes:**
- Weak solution (smaller β) typically for nozzle external shocks
- Strong solution (larger β) represents attached oblique shock

---

## NozzleAnalyzer Class

Location: `aste404_miniproject.nozzle`

Complete nozzle flow analysis with automatic shock detection.

### Initialization

```python
from aste404_miniproject import NozzleAnalyzer, load_inputs, load_geometry

inputs = load_inputs("engine_params.txt")
geometry = load_geometry("nozzle_geom.csv")

analyzer = NozzleAnalyzer(inputs, geometry)
```

**Parameters:**
- `inputs` (dict): Engine parameters including:
  - `'Pc'`: Chamber pressure (Pa)
  - `'Tc'`: Chamber temperature (K)
  - `'gamma'`: Ratio of specific heats
  - `'Pb1'`: Ambient back pressure (Pa)
  
- `geometry_df` (pandas.DataFrame): Nozzle geometry with columns:
  - `'x'`: Axial position (m)
  - `'r'`: Nozzle radius (m)

### Methods

#### `solve_isentropic()`

Solves the isentropic flow field through the nozzle.

**Returns:** None (stores results in instance variables)

**Stores:**
- `self.M`: Mach number at each axial position
- `self.P`: Static pressure at each position (Pa)
- `self.T`: Static temperature at each position (K)

**Algorithm:**
1. Identifies throat (minimum area)
2. Solves subsonic flow upstream (convergent section)
3. Sets M=1 at throat
4. Solves supersonic flow downstream (divergent section)
5. Uses HybridSolver for area-Mach inversion

**Example:**
```python
analyzer.solve_isentropic()
print(f"Exit Mach: {analyzer.M[-1]:.3f}")
print(f"Exit Pressure: {analyzer.P[-1]/1e5:.2f} Bar")
```

#### `detect_shock_type()`

Automatically detects shock regime by comparing exit pressure to ambient.

**Returns:** 
- `'normal'`: Normal shock in divergent section
- `'oblique'`: Overexpanded with external oblique shock
- `None`: Underexpanded (no internal shock)

**Algorithm:**
1. Compares isentropic exit pressure to ambient pressure
2. If overexpanded: scans divergent section
3. For each candidate location: applies normal shock relations
4. Selects shock location with minimum exit pressure error
5. Classifies flow regime

**Stores:**
- `self.shock_type`: Detected regime
- `self.shock_location`: Index in geometry arrays (if normal shock)

**Example:**
```python
shock_type = analyzer.detect_shock_type()
if shock_type == 'normal':
    x_shock = analyzer.x[analyzer.shock_location]
    print(f"Shock at x = {x_shock:.3f} m")
```

#### `plot_results()`

Generates comprehensive multi-panel visualization.

**Displays:**
1. **Nozzle Contour** (top): Geometry with Mach heatmap
2. **Pressure Distribution** (middle): P vs x with post-shock
3. **Temperature Distribution** (bottom left): T vs x
4. **Solver Convergence** (bottom center): Error over iterations
5. **Summary Text** (bottom right): Flow regime and parameters

**Example:**
```python
analyzer.solve_isentropic()
analyzer.detect_shock_type()
analyzer.plot_results()
plt.show()
```

### Instance Variables

**After `solve_isentropic()`:**
- `M`: numpy array, Mach distribution
- `P`: numpy array, Pressure (Pa)
- `T`: numpy array, Temperature (K)
- `x`: numpy array, Axial positions (m)
- `r`: numpy array, Radii (m)
- `A`: numpy array, Area at each position (m²)
- `At`: float, Throat area (m²)
- `throat_idx`: int, Index of throat location

**After `detect_shock_type()`:**
- `shock_type`: str or None
- `shock_location`: int or None
- `M_post_shock`: numpy array (if normal shock)
- `P_post_shock`: numpy array (if normal shock)
- `T_post_shock`: numpy array (if normal shock)

---

## NozzleAnimator Class

Location: `aste404_miniproject.animation`

Animates nozzle flow during atmospheric ascent using US Standard Atmosphere.

### Initialization

```python
from aste404_miniproject import NozzleAnimator

animator = NozzleAnimator(inputs, geometry)
```

### Methods

#### `run()`

Generates and displays animation.

**Process:**
1. Pre-calculates 150 altitude frames (0-30 km)
2. For each frame: updates ambient pressure, solves nozzle flow
3. Animates pressure and Mach distributions
4. Shows shock location evolution
5. Displays real-time flight statistics

**Display:**
- **Top Panel**: Pressure distribution P(x)
- **Bottom Panel**: Mach distribution M(x)
- **Statistics Box**: Altitude, ambient P, exit Mach, flow regime
- **Shock Marker**: Red dashed line showing shock location

**Example:**
```python
animator = NozzleAnimator(inputs, geometry)
animator.run()  # Runs ~50 second animation
```

#### `_get_ambient_pressure(altitude_m)`

Calculates ambient pressure using US Standard Atmosphere 1976.

**Parameters:**
- `altitude_m` (float): Altitude above sea level (m)

**Returns:**
- `float`: Pressure (Pa)

**Altitude Ranges:**
- 0-11 km: Troposphere (temperature lapse)
- 11-20 km: Stratosphere Part 1 (isothermal)
- 20-32 km: Stratosphere Part 2 (temperature inversion)
- >32 km: Simplified exponential model

**Accuracy:** Within 0.1% for standard conditions up to 86 km.

#### `precalculate()`

Pre-computes all 150 frames before animation.

**Features:**
- Progress bar showing calculation status
- Error handling for individual frames
- Shock location and Mach tracking
- Total computation time: ~10-30 seconds

---

## HybridSolver Class

Location: `aste404_miniproject.solver`

Robust numerical root finder for area-Mach relations.

### Initialization

```python
from aste404_miniproject import HybridSolver

solver = HybridSolver(tol=1e-6, max_iter=50)
```

**Parameters:**
- `tol` (float, default 1e-6): Convergence tolerance for |f(x)|
- `max_iter` (int, default 50): Maximum iterations

### Methods

#### `solve(func, deriv, guess, low, high)`

Finds root of f(x)=0 using hybrid Newton-Raphson/Bisection.

**Parameters:**
- `func` (callable): Function f(x)
- `deriv` (callable): Derivative f'(x)
- `guess` (float): Initial guess
- `low` (float): Lower bound (physical limit)
- `high` (float): Upper bound (physical limit)

**Returns:**
- `float`: Root location

**Algorithm:**
1. Attempts Newton step: x_new = x - f(x)/f'(x)
2. If Newton shoots out of bounds: falls back to bisection
3. Tightens bounds each iteration
4. Returns when |f(x)| < tolerance

**Example:**
```python
from aste404_miniproject import HybridSolver, area_mach_relation, area_mach_derivative

solver = HybridSolver()
func = lambda m: area_mach_relation(m, 1.4) - 2.0
deriv = lambda m: area_mach_derivative(m, 1.4)

M = solver.solve(func, deriv, guess=2.5, low=1.0, high=5.0)
print(f"Mach for A/A*=2.0: {M:.4f}")  # ~2.197
```

### Instance Variables

**After `solve()`:**
- `history`: list of |f(x)| at each iteration (for convergence plotting)

---

## Utility Functions

Location: `aste404_miniproject.utils`

### `load_inputs(filepath)`

Loads engine parameters from text file.

**Parameters:**
- `filepath` (str): Path to input file

**Returns:**
- `dict`: Parameters with keys:
  - `'NominalThrust'`: Thrust (N)
  - `'Pb1'`: Ambient pressure (Pa)
  - `'Pc'`: Chamber pressure (Pa)
  - `'Tc'`: Chamber temperature (K)
  - `'gamma'`: Ratio of specific heats
  - `'MW'`: Molar mass (g/mol)
  - And others...

**File Format:**
```
75000     ! Nominal Thrust (N)
101325    ! Ambient Pressure (Pa)
800000    ! Chamber Pressure (Pa)
2800      ! Chamber Temperature (K)
```

### `load_geometry(filepath)`

Loads nozzle geometry from CSV file.

**Parameters:**
- `filepath` (str): Path to CSV file

**Returns:**
- `pandas.DataFrame`: Two columns: 'x' and 'r'

**File Format:**
```csv
x,r
-5.0,2.098
-4.99,2.098
...
1.42,1.42
```

---

## Complete Working Example

```python
import matplotlib.pyplot as plt
from aste404_miniproject import (
    NozzleAnalyzer,
    NozzleAnimator,
    load_inputs,
    load_geometry,
    gas_dynamics,
    HybridSolver
)

# === Gas Dynamics Verification ===
print("1. Gas Dynamics Tests")
c_star_val = gas_dynamics.c_star(gamma=1.2, r=287, t0=2800)
print(f"   c* = {c_star_val:.1f} m/s")

shock = gas_dynamics.normal_shock_relations(M1=2.5, gamma=1.4)
print(f"   Normal shock at M1=2.5: P2/P1={shock['P2_P1']:.3f}, M2={shock['M2']:.3f}")

# === Static Analysis ===
print("\n2. Static Nozzle Analysis (Sea Level)")
inputs = load_inputs("inputs/normal_shock_sealevel_input.txt")
geometry = load_geometry("inputs/Klapsis_Nikitas_nozzle_geometry.csv")

analyzer = NozzleAnalyzer(inputs, geometry)
analyzer.solve_isentropic()
shock_type = analyzer.detect_shock_type()

print(f"   Exit Mach: {analyzer.M[-1]:.3f}")
print(f"   Shock Type: {shock_type}")
if shock_type == 'normal':
    print(f"   Shock Location: x={analyzer.x[analyzer.shock_location]:.3f} m")

analyzer.plot_results()

# === Dynamic Simulation ===
print("\n3. Dynamic Animation (0-30 km)")
animator = NozzleAnimator(inputs, geometry)
animator.run()
```

---

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| `solve_isentropic()` | 0.05-0.2 s | 1000 geometry points |
| `detect_shock_type()` | 0.1-0.5 s | Includes shock solving |
| Pre-calculate 150 frames | 10-30 s | Depends on geometry resolution |
| Animation playback (150 frames) | ~50 s | At 3.3 fps |

---

## Troubleshooting

### "File not found" errors
- Ensure you're running from project root or use absolute paths
- Check file format matches expected input structure

### Solver not converging
- Adjust initial guess closer to expected solution
- Check bounds are physical and bracket the root
- Increase `max_iter` in HybridSolver initialization

### Animation running too fast/slow
- Default interval is 300ms per frame
- Modify in `animation.py`: `interval=300` parameter
- 100ms = fast (10 fps), 500ms = slow (2 fps)

### Unusual shock location
- Check input geometry for smoothness
- Verify ambient pressure is reasonable
- Inspect convergence plot for numerical issues

---

For more examples and detailed usage, see the test files in `/tests/`.
