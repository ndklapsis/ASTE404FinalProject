# Development Guide

## Project Structure

```
ASTE404FinalProject/
├── src/aste404_miniproject/      # Main library package
│   ├── __init__.py               # Package initialization & API export
│   ├── gas_dynamics.py           # Gas dynamics functions (complete toolbox)
│   ├── nozzle.py                 # NozzleAnalyzer class (main simulation)
│   ├── animation.py              # NozzleAnimator class (dynamic sim)
│   ├── solver.py                 # HybridSolver (numerical methods)
│   ├── utils.py                  # I/O utilities
│   ├── design.py                 # Design tools (optional)
│   ├── propellants.py            # Propellant database (optional)
│   └── main.py                   # CLI entry point (optional)
│
├── tests/                        # Test suite
│   ├── test_step1.py            # Gas dynamics verification
│   ├── test_step2.py            # Static nozzle analysis
│   ├── test_step3.py            # Dynamic animation
│   ├── test_normal_shock.py     # Shock detection example
│   └── manualtest.py            # Exploratory tests
│
├── inputs/                       # Example input files
│   ├── Klapsis_Nikitas_input.txt           # Main engine parameters
│   ├── Klapsis_Nikitas_nozzle_geometry.csv # High-res geometry (1000 pts)
│   ├── normal_shock_sealevel_input.txt     # Tuned for sea-level shock
│   ├── sample_input.txt                    # Basic example
│   └── sample_r_vs_x.csv                   # Basic geometry
│
├── README.md                    # Main documentation
├── API.md                       # Complete API reference
├── QUICKSTART.md                # Quick start guide
├── DEVELOPMENT.md               # This file
├── pyproject.toml               # Package configuration
└── LICENSE                      # License

```

---

## Code Organization

### Core Physics Engine: `gas_dynamics.py`

**Purpose:** Complete compressible flow function library

**Structure:**
```python
# 1. Ideal Rocket Functions
def c_star(gamma, r, t0): ...
def c_f(gamma, pe_p0, pa_p0, ae_at): ...

# 2. Isentropic Flow Functions
def area_mach_relation(M, gamma): ...
def area_mach_derivative(M, gamma): ...
def isentropic_P_P0(M, gamma): ...
def isentropic_T_T0(M, gamma): ...
def isentropic_rho_rho0(M, gamma): ...

# 3. Shock Functions
def normal_shock_relations(M1, gamma): ...
def prandtl_meyer_function(M, gamma): ...
def solve_expansion_fan(nu1, nu2, gamma): ...
def solve_oblique_beta(M1, theta, gamma): ...
```

**Key Design Principles:**
- Every function has comprehensive docstrings
- Input validation with meaningful error messages
- Works with both scalars and numpy arrays
- Uses standard variable names (M, P, T, gamma, etc.)
- References formulas in docstrings

---

### Main Analyzer: `nozzle.py`

**Purpose:** Complete nozzle flow analysis with shock detection

**Class: `NozzleAnalyzer`**

```python
class NozzleAnalyzer:
    def __init__(self, inputs: dict, geometry_df):
        """Initialize with engine parameters and geometry"""
    
    def solve_isentropic(self):
        """Calculate isentropic flow field"""
    
    def detect_shock_type(self):
        """Classify flow regime (normal/oblique/underexpanded)"""
    
    def plot_results(self):
        """Generate comprehensive multi-panel visualization"""
    
    # Private methods
    def _find_normal_shock_location(self):
        """Scan for shock location by minimizing exit pressure error"""
    
    def _calculate_normal_shock_flow(self, shock_idx):
        """Calculate post-shock flow field"""
    
    def _generate_shock_summary(self):
        """Create summary text for display"""
    
    def _plot_nozzle_contour(self, ax):
        """Visualize nozzle geometry with Mach heatmap"""
```

**Algorithm: Shock Detection**

1. **Solve isentropic flow** throughout nozzle
2. **Compare exit pressure** to ambient
   - If P_exit > P_ambient: underexpanded, return None
   - If P_exit < P_ambient: overexpanded, proceed
3. **Scan divergent section** point-by-point
4. **For each candidate shock location:**
   - Apply normal shock relations
   - Calculate new stagnation pressure
   - Solve post-shock flow to exit
   - Compute exit pressure
   - Track error: |P_exit - P_ambient|
5. **Select location** with minimum error
6. **Return:** shock_type and shock_location

---

### Animation Engine: `animation.py`

**Purpose:** Dynamic nozzle flow visualization during ascent

**Class: `NozzleAnimator`**

```python
class NozzleAnimator:
    def __init__(self, inputs, geometry):
        """Initialize with standard atmosphere model"""
    
    def run(self):
        """Generate animation with matplotlib FuncAnimation"""
    
    def precalculate(self):
        """Pre-compute all 150 altitude frames"""
    
    def _get_ambient_pressure(self, altitude_m):
        """US Standard Atmosphere 1976 model"""
```

**Atmosphere Model:** Piecewise functions for different altitude ranges
- 0-11 km: Troposphere (linear temperature lapse)
- 11-20 km: Stratosphere Part 1 (isothermal)
- 20-32 km: Stratosphere Part 2 (inverse lapse)
- 32+ km: Exponential decay (simplified)

**Animation Features:**
- 150 frames representing 0-30 km ascent
- Dual-panel display (Pressure + Mach)
- Real-time shock location tracking
- Statistics update each frame
- 300ms interval (3.3 fps) for observation

---

### Numerical Solver: `solver.py`

**Purpose:** Robust root finding for area-Mach relations

**Class: `HybridSolver`**

```python
class HybridSolver:
    def solve(self, func, deriv, guess, low, high):
        """Hybrid Newton-Raphson / Bisection solver"""
        
        # Algorithm:
        # 1. Attempt Newton step: x_new = x - f(x)/f'(x)
        # 2. If out of bounds: use bisection step
        # 3. Tighten bounds each iteration
        # 4. Check convergence: |f(x)| < tol
        # 5. Track iteration history for diagnostics
```

**Key Features:**
- Robust to poor initial guesses
- Falls back to bisection if Newton diverges
- Stores iteration history for convergence plots
- Handles edge cases (zero derivative, NaN, etc.)

---

## Common Development Tasks

### Adding a New Gas Dynamics Function

**Example: Add isothermal pressure drop**

```python
def isothermal_pressure_drop(M, gamma, friction_factor, L_Dh):
    """
    Calculates pressure drop in isothermal flow with friction.
    
    Parameters
    ----------
    M : float
        Mach number at inlet
    gamma : float
        Ratio of specific heats
    friction_factor : float
        Darcy friction factor f
    L_Dh : float
        Ratio of length to hydraulic diameter
    
    Returns
    -------
    float
        Pressure ratio P_out / P_in
    
    References
    ----------
    Shapiro, A.H., et al. "Compressible Flow" (1953)
    """
    # Input validation
    if M <= 0:
        raise ValueError("Mach must be > 0")
    if friction_factor < 0:
        raise ValueError("Friction factor must be >= 0")
    
    # Formula
    term1 = (1 - M**2) / M**2
    term2 = (gamma + 1) / 2 * np.log((2 + (gamma - 1) * M**2) / (gamma + 1))
    term3 = 4 * friction_factor * L_Dh / gamma
    
    P_ratio = np.sqrt(term1 + term2) / np.exp(term3)
    return P_ratio

# Update gas_dynamics.py:
# 1. Add function with docstring and validation
# 2. Export in __init__.py
# 3. Add test in test_step1.py
# 4. Document in API.md
```

---

### Adding Animation Features

**Example: Add temperature contour plot**

```python
# In NozzleAnimator.run():

# Add new subplot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, ...)

# Initialize
line_temp, = ax3.plot([], [], 'r-', lw=2.5, label='Temperature')

# In update function:
T = frame['T']  # Must be stored in frame data
line_temp.set_data(x, T)

# Add to returns
return line_pressure, ..., line_temp
```

---

### Improving Shock Detection

**Current:** Scans divergent section, minimizes pressure error

**Potential improvements:**
1. **Pressure matching tolerance:** Currently ±5%, make configurable
2. **Entropy check:** Verify shock location increases entropy
3. **Multiple shock detection:** Handle double shocks
4. **Boundary layer effects:** Account for displacement thickness

```python
# In detect_shock_type():
tolerance = 0.05  # Make configurable
for i in range(...):
    error = abs(P_exit - P_ambient) / P_ambient
    if error < tolerance:
        return 'normal'
```

---

## Testing Strategy

### Test Pyramid

```
                     Integration Tests (test_step3.py)
                   /
        System Tests (test_step2.py)
      /
   Unit Tests (test_step1.py)
```

**Level 1: Unit Tests** (`test_step1.py`)
- Test individual gas dynamics functions
- Verify against published tables
- Check input validation

**Level 2: System Tests** (`test_step2.py`)
- Load files, run full analysis
- Verify shock detection
- Generate plots

**Level 3: Integration Tests** (`test_step3.py`)
- Run complete animation
- Verify atmosphere model
- Check frame generation

### Adding Tests

```python
# In test_step1.py:

def test_my_new_function():
    """Test new isothermal_pressure_drop function"""
    
    # Test 1: Known values
    P_ratio = isothermal_pressure_drop(M=0.5, gamma=1.4, f=0.02, L_Dh=50)
    expected = 0.953  # From published tables
    assert abs(P_ratio - expected) < 1e-3, f"Got {P_ratio}, expected {expected}"
    
    # Test 2: Edge cases
    with pytest.raises(ValueError):
        isothermal_pressure_drop(M=-1.0, gamma=1.4, f=0.02, L_Dh=50)
    
    # Test 3: Array input
    M_array = np.array([0.3, 0.5, 0.7, 0.9])
    P_array = isothermal_pressure_drop(M_array, 1.4, 0.02, 50)
    assert len(P_array) == len(M_array)
    assert np.all(P_array <= 1.0)  # Pressure decreases
    
    print("✓ All tests passed!")
```

---

## Performance Optimization

### Current Bottlenecks

1. **Solver iterations:** 10-30 per point (1000 points = many calls)
2. **Frame pre-calculation:** 150 frames × expensive analysis
3. **Plotting:** Matplotlib rendering can be slow

### Optimization Strategies

**Quick wins:**
```python
# 1. Cache repeated calculations
self._area_mach_cache = {}

# 2. Use numpy vectorization
self.M = np.zeros(len(self.x))  # Faster than list append

# 3. Skip unnecessary iterations
if shock_error < tolerance:
    break  # Early exit
```

**Advanced:**
```python
# 1. Parallel frame calculation
from multiprocessing import Pool

with Pool(4) as p:
    results = p.map(calculate_frame, altitudes)

# 2. Cython compilation for inner loops
# 3. GPU acceleration for large geometries
```

---

## Documentation Standards

### Docstring Format (NumPy style)

```python
def my_function(param1, param2):
    """
    One-line summary.
    
    Longer description explaining the physical meaning,
    assumptions, and limitations.
    
    Parameters
    ----------
    param1 : type
        Description of param1
    param2 : type
        Description of param2
    
    Returns
    -------
    type
        Description of return value
    
    Raises
    ------
    ValueError
        When inputs are invalid
    
    Notes
    -----
    Physical equation or derivation:
    $$ formula $$
    
    Examples
    --------
    >>> result = my_function(2.5, 1.4)
    >>> print(result)
    1.234
    
    References
    ----------
    [1] Author et al. (Year). Title. Journal.
    """
```

### Code Comments

```python
# Use for non-obvious logic
# Bad: x = x * 2  # Multiply by two
# Good: x = x * 2  # Account for shock stagnation pressure loss

# Use for algorithm steps
for i in range(...):
    # Step 1: Calculate pre-shock conditions
    M_before = self.M[i]
    
    # Step 2: Apply shock relations
    shock_data = normal_shock_relations(M_before, self.gamma)
```

---

## Code Style Guide

### PEP 8 Compliance

```bash
# Check style
pip install flake8
flake8 src/aste404_miniproject/

# Auto-format
pip install black
black src/aste404_miniproject/
```

### Naming Conventions

```python
# Variables: snake_case
chamber_pressure = 800000
exit_mach = 2.5

# Constants: UPPER_CASE
GAMMA_AIR = 1.4
ZERO_TOLERANCE = 1e-6

# Classes: PascalCase
class NozzleAnalyzer:
    pass

# Functions: snake_case
def area_mach_relation(M, gamma):
    pass

# Private methods: _leading_underscore
def _calculate_normal_shock_flow(self):
    pass
```

---

## Release Checklist

- [ ] All tests passing: `pytest tests/`
- [ ] Code formatted: `black src/`
- [ ] Style checked: `flake8 src/`
- [ ] Documentation updated: README.md, API.md
- [ ] Examples tested: QUICKSTART.md
- [ ] Version bumped: `__init__.py`
- [ ] Changelog updated: README.md
- [ ] Git committed: `git commit -am "v0.X.0 release"`
- [ ] Git tagged: `git tag v0.X.0`
- [ ] Pushed: `git push origin main --tags`

---

## Contributing Guidelines

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Code** with style compliance
4. **Test** thoroughly
5. **Document** with docstrings and examples
6. **Commit** with clear messages: `git commit -am "Add feature X"`
7. **Push** to your fork
8. **Create** Pull Request with description

**Before submitting:**
- [ ] Functions have docstrings
- [ ] Examples work
- [ ] Tests pass
- [ ] Code formatted
- [ ] No warnings/errors

---

## Troubleshooting Development Issues

### Import Errors
```python
# Problem: "No module named 'aste404_miniproject'"
# Solution:
cd ASTE404FinalProject
pip install -e .
```

### Solver Not Converging
```python
# Problem: Solver stuck at max iterations
# Solution: Increase tolerance or max_iter
solver = HybridSolver(tol=1e-5, max_iter=100)
```

### Matplotlib Issues
```python
# Problem: Plots not showing in Jupyter
# Solution: Use %matplotlib inline magic
%matplotlib inline

# Problem: Animation frozen
# Solution: Use blit=False for debugging
ani = FuncAnimation(..., blit=False)
```

---

## Future Enhancements

### Phase 2: Advanced Physics
- [ ] Viscous flow with wall friction
- [ ] Heat transfer (internal/external)
- [ ] Two-phase flow (particles)
- [ ] Real gas effects (non-ideal)
- [ ] Chemical reactions (non-frozen flow)

### Phase 3: Optimization & Design
- [ ] Automatic nozzle design (optimize Ae/At for given Pc, Tc)
- [ ] Multi-objective optimization (thrust vs. efficiency)
- [ ] Sensitivity analysis (parametric studies)
- [ ] Design visualization

### Phase 4: Integration
- [ ] Web interface (Flask/Django)
- [ ] Desktop GUI (PyQt/Tkinter)
- [ ] Export to CAD (STEP/IGES)
- [ ] Database of propellants
- [ ] Cloud computing interface

---

**Happy developing! 🚀**
