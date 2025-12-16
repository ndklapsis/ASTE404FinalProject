# ASTE 404 Nozzle Simulation Toolbox

A comprehensive Python library for **gas dynamics analysis**, **rocket nozzle simulation**, and **dynamic atmospheric animation**. This toolbox provides a complete suite of tools for analyzing compressible flow through convergent-divergent nozzles, including shock detection, normal shock relations, and isentropic flow calculations.

## Features

- ✅ **Gas Dynamics Toolbox**: Complete set of compressible flow functions
- ✅ **Nozzle Analysis**: Isentropic and shock flow analysis with automatic shock detection
- ✅ **Shock Detection**: Normal, oblique, and underexpanded flow regime classification
- ✅ **Dynamic Animation**: Real-time visualization of nozzle behavior during atmospheric ascent
- ✅ **Standard Atmosphere Model**: US Standard Atmosphere 1976 for realistic simulations
- ✅ **Fully Documented**: Comprehensive docstrings and examples for every module
- ✅ **Production-Ready**: Input validation, error handling, and robust numerical methods

## Installation

### Requirements
- Python 3.8+
- NumPy
- Pandas
- Matplotlib

### Install from Source

```bash
git clone https://github.com/ndklapsis/ASTE404FinalProject.git
cd ASTE404FinalProject
pip install -e .
```

Or install dependencies manually:
```bash
pip install numpy pandas matplotlib
```

## Quick Start

### 1. Gas Dynamics Calculations

```python
from aste404_miniproject import gas_dynamics

# Calculate characteristic velocity
c_star = gas_dynamics.c_star(gamma=1.2, r=287, t0=2800)
print(f"c*: {c_star:.2f} m/s")

# Isentropic pressure ratio
P_ratio = gas_dynamics.isentropic_P_P0(M=2.5, gamma=1.4)
print(f"P/P0 at M=2.5: {P_ratio:.4f}")

# Normal shock relations
shock_data = gas_dynamics.normal_shock_relations(M1=2.5, gamma=1.4)
print(f"M2 = {shock_data['M2']:.3f}, P2/P1 = {shock_data['P2_P1']:.3f}")

# Area-Mach relation
A_Astar = gas_dynamics.area_mach_relation(M=2.0, gamma=1.4)
print(f"A/A* = {A_Astar:.3f}")
```

### 2. Single Nozzle Analysis

```python
from aste404_miniproject import NozzleAnalyzer, load_inputs, load_geometry

# Load input parameters and geometry
inputs = load_inputs("inputs/engine_input.txt")
geometry = load_geometry("inputs/nozzle_geometry.csv")

# Create analyzer
analyzer = NozzleAnalyzer(inputs, geometry)

# Solve isentropic flow
analyzer.solve_isentropic()

# Detect shock type
shock_type = analyzer.detect_shock_type()

# Display results
analyzer.plot_results()
```

### 3. Dynamic Animation (Atmospheric Ascent)

```python
from aste404_miniproject import NozzleAnimator, load_inputs, load_geometry

# Load parameters
inputs = load_inputs("inputs/engine_input.txt")
geometry = load_geometry("inputs/nozzle_geometry.csv")

# Create animator with standard atmosphere
animator = NozzleAnimator(inputs, geometry)

# Run animation (0-30 km altitude with 150 frames)
animator.run()
```

## Module Documentation

### `gas_dynamics` - Compressible Flow Functions

The core physics engine for all calculations.

#### Ideal Rocket Functions
- **`c_star(gamma, r, t0)`** - Characteristic velocity
- **`c_f(gamma, pe_p0, pa_p0, ae_at)`** - Thrust coefficient

#### Isentropic Flow Functions
- **`area_mach_relation(M, gamma)`** - Normalized area (A/A*)
- **`area_mach_derivative(M, gamma)`** - Derivative for solver
- **`isentropic_P_P0(M, gamma)`** - Pressure ratio (P/P0)
- **`isentropic_T_T0(M, gamma)`** - Temperature ratio (T/T0)
- **`isentropic_rho_rho0(M, gamma)`** - Density ratio (ρ/ρ0)

#### Shock Functions
- **`normal_shock_relations(M1, gamma)`** - Normal shock across all parameters
- **`prandtl_meyer_function(M, gamma)`** - Prandtl-Meyer angle (degrees)
- **`solve_expansion_fan(nu1, nu2, gamma)`** - Expansion fan solution
- **`solve_oblique_beta(M1, theta, gamma)`** - Oblique shock solution

### `NozzleAnalyzer` - Single Nozzle Simulation

Complete nozzle flow analysis with automatic shock detection.

```python
analyzer = NozzleAnalyzer(inputs, geometry_df)
analyzer.solve_isentropic()          # Calculate isentropic flow
shock_type = analyzer.detect_shock_type()  # Detect shock regime
analyzer.plot_results()              # Display comprehensive plots
```

**Shock Types:**
- `'normal'` - Normal shock in divergent section
- `'oblique'` - Overexpanded with external shock structure
- `None` - Underexpanded (no internal shock)

**Output Arrays:**
- `analyzer.M` - Mach number distribution
- `analyzer.P` - Static pressure distribution (Pa)
- `analyzer.T` - Static temperature distribution (K)
- `analyzer.M_post_shock` - Mach after shock (if normal shock)
- `analyzer.P_post_shock` - Pressure after shock (if normal shock)
- `analyzer.shock_location` - Index of shock location

### `NozzleAnimator` - Dynamic Atmospheric Simulation

Animate nozzle flow evolution during rocket ascent using standard atmosphere.

```python
animator = NozzleAnimator(inputs, geometry_df)
animator.run()  # Generates 150 frames from 0-30 km altitude
```

**Features:**
- US Standard Atmosphere 1976 model
- Real-time pressure and Mach visualization
- Shock location tracking during ascent
- Automatic flow regime classification

### `HybridSolver` - Numerical Root Finder

Robust hybrid Newton-Raphson/Bisection solver for area-Mach relations.

```python
from aste404_miniproject import HybridSolver

solver = HybridSolver(tol=1e-6, max_iter=50)
func = lambda m: area_mach_relation(m, 1.4) - 2.0
deriv = lambda m: area_mach_derivative(m, 1.4)

M = solver.solve(func, deriv, guess=2.5, low=1.0, high=5.0)
```

### `utils` - Input/Output Functions

- **`load_inputs(filepath)`** - Load engine parameters from text file
- **`load_geometry(filepath)`** - Load nozzle geometry from CSV

## Input File Format

### Engine Parameters (`input.txt`)

```plaintext
75000     ! Nominal Thrust (N)
101325    ! Ambient Pressure (Pa)
800000    ! Chamber Pressure (Pa)
2800      ! Chamber Temperature (K)
1.25      ! Specific Heat Ratio (gamma)
28        ! Molar Mass (g/mol)
0.34      ! Nozzle Contour Coefficient a
0.0034    ! Nozzle Contour Coefficient b
0.00034   ! Nozzle Contour Coefficient c
0.6       ! R_wtd
0.5       ! R_wtu
0.3       ! R_i
33        ! theta_i (deg)
4.4       ! Contraction Area Ratio CR
```

### Nozzle Geometry (`geometry.csv`)

```csv
x,r
-5.0,2.098
-4.99,2.098
...
1.42,1.42
```
Where:
- `x` = Axial position (m)
- `r` = Radius at position (m)

## Output Files

The animation produces:
- Real-time plots showing pressure, Mach, and shock evolution
- Convergence plots for numerical solver validation
- Summary statistics for each altitude

## Example: Complete Workflow

```python
import os
from aste404_miniproject import (
    NozzleAnalyzer, 
    NozzleAnimator,
    load_inputs, 
    load_geometry,
    gas_dynamics
)

# === Step 1: Gas Dynamics Verification ===
print("Testing gas dynamics...")
M_test = gas_dynamics.area_mach_relation(2.0, 1.4)
print(f"A/A* at M=2.0: {M_test:.4f}")

# === Step 2: Static Nozzle Analysis ===
print("\nAnalyzing nozzle at sea level...")
inputs = load_inputs("inputs/nozzle_input.txt")
geometry = load_geometry("inputs/nozzle_geometry.csv")

analyzer = NozzleAnalyzer(inputs, geometry)
analyzer.solve_isentropic()
shock_type = analyzer.detect_shock_type()

print(f"Shock type: {shock_type}")
print(f"Exit Mach: {analyzer.M[-1]:.3f}")
print(f"Exit Pressure: {analyzer.P[-1]/1e5:.3f} Bar")

if shock_type == 'normal':
    print(f"Shock location: x = {analyzer.x[analyzer.shock_location]:.3f} m")
    analyzer.plot_results()

# === Step 3: Dynamic Simulation ===
print("\nRunning atmospheric ascent animation...")
animator = NozzleAnimator(inputs, geometry)
animator.run()
```

## Testing

Run the test suite:

```bash
# Step 1: Gas dynamics verification
python tests/test_step1.py

# Step 2: Static nozzle analysis with plots
python tests/test_step2.py

# Step 3: Dynamic animation
python tests/test_step3.py

# Normal shock at sea level (example)
python tests/test_normal_shock.py
```

## Theory & Physics

### Isentropic Flow Relations

For reversible, adiabatic flow:
$$\frac{A}{A^*} = \frac{1}{M}\left[\frac{2}{\gamma+1}\left(1 + \frac{\gamma-1}{2}M^2\right)\right]^{(\gamma+1)/(2(\gamma-1))}$$

### Normal Shock Relations

Across a normal shock:
$$M_2^2 = \frac{2 + (\gamma-1)M_1^2}{2\gamma M_1^2 - (\gamma-1)}$$

$$\frac{P_2}{P_1} = 1 + \frac{2\gamma}{\gamma+1}(M_1^2 - 1)$$

$$\frac{P_{02}}{P_{01}} = \frac{(2\gamma M_1^2 - (\gamma-1))(\gamma+1)}{((\gamma+1)M_1)^2} \cdot \frac{1}{\left[1 + \frac{\gamma-1}{2}M_1^2\right]}$$

### Shock Detection Algorithm

The analyzer uses a robust scanning algorithm to detect normal shock location:
1. Calculate isentropic flow throughout nozzle
2. Compare exit pressure to ambient pressure
3. If overexpanded: scan divergent section for shock location
4. For each candidate location, apply normal shock relations
5. Select location that minimizes pressure error at exit
6. Return shock location and type

## Limitations & Assumptions

- **Quasi-1D flow**: Assumes flow properties are uniform across cross-section
- **Ideal gas**: Uses ideal gas law; not suitable for dense gases or plasmas
- **No boundary layers**: Inviscid analysis; does not account for friction losses
- **Frozen chemistry**: Assumes constant γ and molecular weight throughout nozzle
- **Atmosphere model**: Valid up to 86 km altitude (above that, simplified exponential)

## Performance Notes

- Pre-calculates 150 altitude frames in ~10-30 seconds (depending on geometry resolution)
- Animation runs at 3.3 fps for detailed observation of transient behavior
- Solver converges in 10-30 iterations for typical nozzle geometries

## Contributing

Contributions welcome! Areas for enhancement:
- Viscous flow corrections (CFD validation)
- Two-phase flow (particle laden jets)
- Heat transfer effects
- Chemical non-equilibrium
- Web interface for interactive design

## License

This project is for educational use in ASTE 404 Mini-Project course.

## References

1. Anderson, J.D. (2003). *Modern Compressible Flow with Historical Perspective*
2. Sutton, G.P. & Biblarz, O. (2016). *Rocket Propulsion Elements*
3. NACA Report 1135 - Equations, Tables, and Charts for Compressible Flow
4. US Standard Atmosphere (1976) - NASA/NOAA Standard

## Author

Nikitas Klapsis  
ASTE 404 Mini-Project, Fall 2025

## Changelog

### v0.3.0 (Current)
- ✅ Complete gas dynamics toolbox with full documentation
- ✅ Robust nozzle analyzer with shock detection
- ✅ Dynamic animation with standard atmosphere
- ✅ Comprehensive README and examples
- ✅ Production-ready error handling

### v0.2.0
- Added shock detection and animation framework
- Implemented standard atmosphere model

### v0.1.0
- Initial gas dynamics functions and solver