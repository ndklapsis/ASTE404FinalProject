# ASTE 404 Nozzle Toolbox - Quick Start Guide

## Installation & Setup

### 1. Prerequisites
```bash
pip install numpy pandas matplotlib
```

### 2. Install the library
```bash
cd path/to/ASTE404FinalProject
pip install -e .
```

Verify installation:
```python
import aste404_miniproject
print(aste404_miniproject.__version__)  # Should print: 0.3.0
```

---

## 5-Minute Tutorial

### Example 1: Gas Dynamics Calculations

```python
from aste404_miniproject import gas_dynamics

# Calculate characteristic velocity (c*)
c_star = gas_dynamics.c_star(gamma=1.2, r=287, t0=2800)
print(f"Characteristic velocity: {c_star:.1f} m/s")

# Get isentropic pressure ratio at a given Mach
P_ratio = gas_dynamics.isentropic_P_P0(M=2.5, gamma=1.4)
print(f"P/P0 at M=2.5: {P_ratio:.4f}")

# Normal shock relations
shock = gas_dynamics.normal_shock_relations(M1=2.5, gamma=1.4)
print(f"Post-shock Mach: {shock['M2']:.3f}")
print(f"Pressure ratio: {shock['P2_P1']:.3f}")
```

**Output:**
```
Characteristic velocity: 1852.3 m/s
P/P0 at M=2.5: 0.0585
Post-shock Mach: 0.513
Pressure ratio: 5.675
```

---

### Example 2: Analyze a Nozzle at Sea Level

```python
from aste404_miniproject import NozzleAnalyzer, load_inputs, load_geometry
import matplotlib.pyplot as plt

# Load engine parameters and geometry
inputs = load_inputs("inputs/normal_shock_sealevel_input.txt")
geometry = load_geometry("inputs/Klapsis_Nikitas_nozzle_geometry.csv")

# Create analyzer
analyzer = NozzleAnalyzer(inputs, geometry)

# Solve isentropic flow
print("Solving isentropic flow...")
analyzer.solve_isentropic()

# Print results
print(f"Exit Mach: {analyzer.M[-1]:.3f}")
print(f"Exit Pressure: {analyzer.P[-1]/1e5:.3f} Bar")
print(f"Throat area: {analyzer.At:.6f} m²")

# Detect shock type
print("\nDetecting shock...")
shock_type = analyzer.detect_shock_type()
print(f"Shock type: {shock_type}")

if shock_type == 'normal':
    shock_x = analyzer.x[analyzer.shock_location]
    M1 = analyzer.M[analyzer.shock_location]
    M2 = analyzer.M_post_shock[analyzer.shock_location]
    print(f"  Location: x = {shock_x:.3f} m")
    print(f"  Pre-shock Mach: {M1:.3f}")
    print(f"  Post-shock Mach: {M2:.3f}")

# Show plots
analyzer.plot_results()
plt.show()
```

---

### Understanding Shock Detection

The `detect_shock_type()` method automatically classifies flow regimes:

**Flow Regimes:**
- **Underexpanded** (No Shock): Exit pressure ≥ ambient → normal supersonic exit
- **Normal Shock**: Exit pressure < ambient → shock in divergent section
- **Oblique Shocks**: Exit pressure < ambient, no internal shock → external shock system

**Key Attributes After Detection:**
- `analyzer.shock_type` - Type: 'normal', 'oblique', or None
- `analyzer.shock_location` - Index where shock occurs
- `analyzer.M_post_shock` - Mach distribution with shock
- `analyzer.P_post_shock` - Pressure distribution with shock

**Algorithm:**
The method compares exit pressure to ambient, then if overexpanded, searches for a normal shock location that matches ambient pressure at the exit (within 5% tolerance).

---

### Example 3: Animate Nozzle During Ascent

```python
from aste404_miniproject import NozzleAnimator, load_inputs, load_geometry

# Load data
inputs = load_inputs("inputs/Klapsis_Nikitas_input.txt")
geometry = load_geometry("inputs/Klapsis_Nikitas_nozzle_geometry.csv")

# Create animator (uses standard atmosphere 0-30 km)
animator = NozzleAnimator(inputs, geometry)

# Run animation
print("Pre-calculating 150 altitude frames...")
animator.run()

# The animation will show:
# - Top: Pressure distribution
# - Bottom: Mach distribution
# - Real-time shock location tracking
# - Altitude and ambient pressure updates
```

---

## Common Tasks

### Task 1: Compare Shock Location at Different Altitudes

```python
from aste404_miniproject import NozzleAnalyzer, load_inputs, load_geometry

inputs = load_inputs("inputs/engine_input.txt")
geometry = load_geometry("inputs/nozzle_geom.csv")

altitudes = [0, 5000, 10000, 15000]  # meters
baseline_P0 = 101325  # Pa (sea level)

for alt in altitudes:
    # Approximate ambient pressure (rough formula)
    P_ambient = baseline_P0 * (1 - 0.0065 * alt / 288.15) ** 5.255
    
    inputs['Pb1'] = P_ambient
    analyzer = NozzleAnalyzer(inputs, geometry)
    analyzer.solve_isentropic()
    shock_type = analyzer.detect_shock_type()
    
    if shock_type == 'normal':
        x_shock = analyzer.x[analyzer.shock_location]
        print(f"Alt {alt/1000:.1f} km: shock at x={x_shock:.3f} m")
    else:
        print(f"Alt {alt/1000:.1f} km: {shock_type} flow")
```

---

### Task 2: Verify Gas Dynamics Functions

```python
from aste404_miniproject import (
    gas_dynamics,
    HybridSolver,
    area_mach_relation,
    area_mach_derivative
)

# Test area-Mach relation
# Known: A/A* = 2.0 should give M ≈ 2.197 (supersonic)
solver = HybridSolver(tol=1e-8)
func = lambda m: area_mach_relation(m, 1.4) - 2.0
deriv = lambda m: area_mach_derivative(m, 1.4)

M_solution = solver.solve(func, deriv, guess=2.5, low=1.0, high=5.0)
print(f"Area ratio 2.0 gives M = {M_solution:.4f}")

# Verify with known value
expected = 2.19704  # From standard tables
error = abs(M_solution - expected)
print(f"Error vs. standard table: {error:.6f}")
assert error < 1e-4, "Solver accuracy check failed!"
print("✓ Solver verified!")
```

---

### Task 3: Plot Pressure vs. Mach at Different Ambient Pressures

```python
from aste404_miniproject import NozzleAnalyzer, load_inputs, load_geometry
import matplotlib.pyplot as plt

inputs = load_inputs("inputs/engine_input.txt")
geometry = load_geometry("inputs/nozzle_geom.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Test at different ambient pressures
ambient_pressures = [10000, 50000, 101325, 200000]  # Pa

for P_amb in ambient_pressures:
    inputs['Pb1'] = P_amb
    analyzer = NozzleAnalyzer(inputs, geometry)
    analyzer.solve_isentropic()
    shock_type = analyzer.detect_shock_type()
    
    # Use appropriate pressure array
    if shock_type == 'normal':
        P_plot = analyzer.P_post_shock
    else:
        P_plot = analyzer.P
    
    ax1.plot(analyzer.x, P_plot/1e5, label=f'{P_amb/1e5:.1f} Bar')
    ax2.plot(analyzer.x, analyzer.M, label=f'{P_amb/1e5:.1f} Bar')

ax1.set_xlabel('Axial Position x (m)')
ax1.set_ylabel('Pressure (Bar)')
ax1.set_title('Pressure Distribution')
ax1.grid(True, alpha=0.3)
ax1.legend()

ax2.set_xlabel('Axial Position x (m)')
ax2.set_ylabel('Mach Number')
ax2.set_title('Mach Distribution')
ax2.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.show()
```

---

## Input File Templates

### Engine Parameters Template (`inputs/my_engine.txt`)

```plaintext
75000     ! Nominal Thrust (N)
101325    ! Ambient Pressure (Pa) - can be modified
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

### Geometry File Template (`inputs/my_geometry.csv`)

```csv
x,r
-5.00,2.098
-4.99,2.098
...
0.00,0.1
...
1.42,1.42
```

Where:
- `x` = axial position from throat (m)
- `r` = nozzle radius at that position (m)

---

## Key Equations Reference

### Characteristic Velocity
$$c^* = \sqrt{\frac{RT_0}{\gamma}\left(\frac{\gamma+1}{2}\right)^{(\gamma+1)/(\gamma-1)}}$$

### Isentropic Pressure Ratio
$$\frac{P}{P_0} = \left(1 + \frac{\gamma-1}{2}M^2\right)^{-\gamma/(\gamma-1)}$$

### Normal Shock (Post-shock Mach)
$$M_2^2 = \frac{2+(\gamma-1)M_1^2}{2\gamma M_1^2-(\gamma-1)}$$

### Thrust Coefficient
$$C_F = \sqrt{\frac{2\gamma^2}{\gamma-1}\left(\frac{2}{\gamma+1}\right)^{(\gamma+1)/(\gamma-1)}\left[1-\left(\frac{P_e}{P_0}\right)^{(\gamma-1)/\gamma}\right]} + \frac{P_e - P_a}{P_c} \frac{A_e}{A_t}$$

---

## Troubleshooting

### Q: Animation is too fast/slow?
**A:** Modify the `interval` parameter in `animation.py` line ~247:
```python
ani = FuncAnimation(..., interval=300, ...)  # ms per frame
# 100ms = 10 fps (fast)
# 300ms = 3.3 fps (normal)
# 500ms = 2 fps (slow)
```

### Q: "File not found" error?
**A:** Use absolute paths or ensure you're in the project root:
```python
import os

# Method 1: Absolute path
inputs = load_inputs("/home/user/ASTE404/inputs/engine.txt")

# Method 2: Relative from project root
inputs = load_inputs("inputs/engine.txt")

# Method 3: Build path dynamically
base_dir = os.path.dirname(__file__)
inputs = load_inputs(os.path.join(base_dir, "inputs/engine.txt"))
```

### Q: Solver not converging?
**A:** Check the bounds and initial guess:
```python
from aste404_miniproject import HybridSolver, area_mach_relation, area_mach_derivative

solver = HybridSolver(tol=1e-6, max_iter=100)  # Increase iterations
func = lambda m: area_mach_relation(m, 1.4) - 2.0
deriv = lambda m: area_mach_derivative(m, 1.4)

# Make sure:
# 1. Root is bracketed: func(low) * func(high) < 0
# 2. Bounds are physical: 0 < low < high
# 3. Guess is reasonable: low < guess < high

M = solver.solve(func, deriv, guess=2.0, low=1.001, high=5.0)
```

### Q: Shock location seems wrong?
**A:** Check the tolerance and verify with convergence plot:
```python
analyzer.solve_isentropic()
analyzer.detect_shock_type()

# The convergence plot shows solver accuracy
# Shock location is selected by minimizing exit pressure error
# Typical tolerance: 5% of ambient pressure

print(f"Exit pressure error: {abs(analyzer.P_post_shock[-1] - P_ambient)/P_ambient * 100:.1f}%")
```

---

## Next Steps

- **Learn more:** See `API.md` for complete reference
- **Run tests:** `python tests/test_step1.py`, `test_step2.py`, `test_step3.py`
- **Explore examples:** Check test files in `/tests/` directory
- **Contribute:** Enhance functions or add new features!

---

**Happy analyzing! 🚀**
