# Library Documentation Index

## Complete Documentation Set

This is your complete guide to the ASTE 404 Nozzle Simulation Toolbox. Below is an organized index of all documentation files.

---

## Getting Started

1. **[README.md](README.md)** - Main documentation
   - Feature overview
   - Quick installation
   - Quick start overview
   - Theory & physics background
   - Limitations & assumptions

2. **[QUICKSTART.md](QUICKSTART.md)** - Complete setup & tutorial
   - Installation & verification
   - Three complete working examples
   - Shock detection guide
   - Common tasks with code
   - Input file templates
   - Key equations reference
   - Troubleshooting FAQ

---

## 📖 Reference Documentation

3. **[API.md](API.md)** - Complete API reference (75+ pages)
   - `gas_dynamics` module (all functions with formulas)
   - `NozzleAnalyzer` class (detailed methods)
   - `NozzleAnimator` class (dynamic simulation)
   - `HybridSolver` class (numerical methods)
   - Utility functions
   - Performance benchmarks
   - Complete working examples

4. **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guide
   - Project structure & organization
   - Code design principles
   - Contributing guidelines
   - Testing strategy
   - Performance optimization
   - Documentation standards
   - Release checklist

---

## 📁 Code Organization

```
src/aste404_miniproject/
├── __init__.py           ← Main API exports
├── gas_dynamics.py       ← Physics functions (415 lines)
├── nozzle.py            ← Nozzle analyzer (436 lines)
├── animation.py         ← Dynamic animation (260 lines)
├── solver.py            ← Numerical solver (100 lines)
├── utils.py             ← I/O utilities
├── design.py            ← ⚠️ DEPRECATED (will be functional in v0.4)
├── propellants.py       ← ⚠️ DEPRECATED (will be functional in v0.4)
└── main.py              ← CLI interface (optional)
```

> **Note:** `design.py` and `propellants.py` are not yet functional. These modules will be available in version 0.4. For now, use the core modules above.

---

## Test Files

Located in `/tests/`:

1. **test_step1.py** - Gas dynamics verification
   - Unit tests for all physics functions
   - Validates against published tables
   - ~50 test cases

2. **test_step2.py** - Static nozzle analysis
   - Load engine parameters
   - Solve nozzle flow
   - Detect shock type
   - Generate plots

3. **test_step3.py** - Dynamic animation
   - Pre-calculate altitude frames
   - Run atmospheric animation
   - Verify shock evolution

4. **test_normal_shock.py** - Shock detection example
   - Load tuned engine for sea-level shock
   - Verify shock location
   - Display results

---

## Example Input Files

Located in `/inputs/`:

1. **Klapsis_Nikitas_input.txt** (Primary engine)
   - 1390 kPa chamber pressure
   - 2700 K chamber temperature
   - Produces shock at altitude

2. **Klapsis_Nikitas_nozzle_geometry.csv** (High-resolution)
   - 1000 geometry points
   - Expansion ratio ~200:1
   - Complete convergent-divergent nozzle

3. **normal_shock_sealevel_input.txt** (Tuned example)
   - 800 kPa chamber pressure
   - Produces normal shock at sea level (101.3 kPa)
   - Perfect for learning

4. **sample_input.txt** & **sample_r_vs_x.csv** (Simple examples)
   - Basic geometry
   - Good for testing

---

## Quick Navigation by Task

### Task: Install and Verify
1. Read: INSTALL.md
2. Run: `pip install -e .`
3. Verify: `python tests/test_step1.py`

### Task: Learn the Basics
1. Read: QUICKSTART.md
2. Try: Example 1 (Gas Dynamics)
3. Try: Example 2 (Nozzle Analysis)

### Task: Use for Research
1. Read: API.md (Module references)
2. Try: test_step2.py
3. Modify input files
4. Generate plots

### Task: Create Animation
1. Read: QUICKSTART.md (Example 3)
2. Run: test_step3.py
3. Modify animation parameters
4. Study atmosphere model

### Task: Add New Features
1. Read: DEVELOPMENT.md
2. Study: Code organization section
3. Follow: Contributing guidelines
4. Add tests for your code

### Task: Troubleshoot Issues
1. Check: INSTALL.md (Troubleshooting)
2. Check: QUICKSTART.md (FAQ)
3. Check: API.md (Usage examples)
4. Run: test files to isolate problem

---

## Module Documentation Quick Reference

### `gas_dynamics` Functions (8 categories)

**Ideal Rocket:**
- `c_star()` - Characteristic velocity
- `c_f()` - Thrust coefficient

**Isentropic Flow:**
- `area_mach_relation()` - A/A* vs M
- `area_mach_derivative()` - d(A/A*)/dM
- `isentropic_P_P0()` - P/P0 vs M
- `isentropic_T_T0()` - T/T0 vs M
- `isentropic_rho_rho0()` - ρ/ρ0 vs M

**Shock & Expansion:**
- `normal_shock_relations()` - Complete shock properties
- `prandtl_meyer_function()` - Prandtl-Meyer angle
- `solve_expansion_fan()` - Expansion fan analysis
- `solve_oblique_beta()` - Oblique shock solver

### Main Classes

**NozzleAnalyzer** (Static Analysis)
- `solve_isentropic()` - Calculate flow field
- `detect_shock_type()` - Classify regime
- `plot_results()` - Visualize

**NozzleAnimator** (Dynamic Simulation)
- `run()` - Generate animation
- `precalculate()` - Pre-compute frames

**HybridSolver** (Numerical Methods)
- `solve()` - Find roots of equations
