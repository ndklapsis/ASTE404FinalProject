"""
ASTE 404 Nozzle Simulation Toolbox

A comprehensive Python library for gas dynamics analysis, rocket nozzle simulation,
and dynamic atmospheric animation. This module provides:

- Gas Dynamics Toolbox: Complete compressible flow functions
- Nozzle Analysis: Isentropic and shock flow analysis with automatic shock detection
- Shock Detection: Normal, oblique, and underexpanded flow regime classification
- Dynamic Animation: Real-time visualization during atmospheric ascent
- Standard Atmosphere: US Standard Atmosphere 1976 model

Quick Start:
-----------

1. Gas Dynamics (compressible flow calculations):

    from aste404_miniproject import gas_dynamics
    c_star = gas_dynamics.c_star(gamma=1.2, r=287, t0=2800)
    shock = gas_dynamics.normal_shock_relations(M1=2.5, gamma=1.4)

2. Single Nozzle Analysis:

    from aste404_miniproject import NozzleAnalyzer, load_inputs, load_geometry
    inputs = load_inputs("engine_input.txt")
    geo = load_geometry("nozzle_geometry.csv")
    analyzer = NozzleAnalyzer(inputs, geo)
    analyzer.solve_isentropic()
    analyzer.plot_results()

3. Dynamic Animation:

    from aste404_miniproject import NozzleAnimator
    animator = NozzleAnimator(inputs, geo)
    animator.run()  # Animates 0-30 km ascent

For detailed documentation, see README.md or call help() on any function/class.
"""

__version__ = "0.3.0"
__author__ = "Nikitas Klapsis"
__license__ = "Educational Use - ASTE 404"

# Core numerical solver
from .solver import HybridSolver

# Main analysis classes
from .nozzle import NozzleAnalyzer
from .animation import NozzleAnimator

# Gas dynamics functions (complete set)
from . import gas_dynamics
from .gas_dynamics import (
    # Ideal rocket functions
    c_star,
    c_f,
    # Isentropic flow
    area_mach_relation,
    area_mach_derivative,
    isentropic_P_P0,
    isentropic_T_T0,
    # Shock relations
    normal_shock_relations,
    prandtl_meyer_function,
    solve_expansion_fan,
    solve_oblique_beta,
)

# Utility functions
from .utils import load_inputs, load_geometry

# Public API
__all__ = [
    # Version
    "__version__",
    
    # Main Classes
    "HybridSolver",
    "NozzleAnalyzer",
    "NozzleAnimator",
    
    # Gas Dynamics (functions)
    "gas_dynamics",  # Full module
    "c_star",
    "c_f",
    "area_mach_relation",
    "area_mach_derivative",
    "isentropic_P_P0",
    "isentropic_T_T0",
    "isentropic_rho_rho0",
    "normal_shock_relations",
    "prandtl_meyer_function",
    "solve_expansion_fan",
    "solve_oblique_beta",
    
    # Utilities
    "load_inputs",
    "load_geometry",
]