# ASTE 404 Nozzle Simulation Toolbox

A comprehensive Python library for **gas dynamics analysis**, **rocket nozzle simulation**, and **dynamic atmospheric animation**. This toolbox provides a complete suite of tools for analyzing compressible flow through convergent-divergent nozzles, including shock detection, normal shock relations, and isentropic flow calculations. This toolbox can be used as just a mathematics library for common gas dynamics equations, a single nozzle analysis tool for pressures/temperatures/shocks, or a dynamic simulation of a nozzle as it travels through a standard atmosphere. 

## Features

- **Gas Dynamics Toolbox**: Complete set of compressible flow functions
- **Nozzle Analysis**: Isentropic and shock flow analysis with automatic shock detection
- **Shock Detection**: Normal, oblique, and underexpanded flow regime classification
- **Dynamic Animation**: Real-time visualization of nozzle behavior during atmospheric ascent

## Quick Installation

**Requirements:** Python 3.8+, NumPy, Pandas, Matplotlib

```bash
pip install -e .
```

For full setup instructions and verification, see **[QUICKSTART.md](QUICKSTART.md)**.

## Quick Start

Three main use cases:

**1. Gas Dynamics Calculations** - Use compressible flow functions directly
**2. Single Nozzle Analysis** - Load engine and geometry, solve and plot
**3. Dynamic Animation** - Simulate nozzle behavior during atmospheric ascent

See **[QUICKSTART.md](QUICKSTART.md)** for complete working examples with output.

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
- Added dynamic animation with standard atmosphere

### v0.2.0
- Added shock detection and animation framework
- Implemented standard atmosphere model

### v0.1.0
- Initial gas dynamics functions and solver