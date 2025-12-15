"""
ASTE 404 Mini-Project Library
Step 2: Nozzle Analysis
"""

from .solver import HybridSolver
from .nozzle import NozzleAnalyzer  # <--- NEW
from .utils import load_inputs, load_geometry # <--- NEW
from .gas_dynamics import (
    area_mach_relation, 
    normal_shock_relations, 
    solve_expansion_fan, 
    solve_oblique_beta
)

__version__ = "0.2.0"