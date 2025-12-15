"""
ASTE 404 Mini-Project Library
Step 1: Core Physics & Solver
"""

from .solver import HybridSolver
from .gas_dynamics import (
    area_mach_relation, 
    normal_shock_relations, 
    solve_expansion_fan, 
    solve_oblique_beta
)

__version__ = "0.1.0"