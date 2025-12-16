"""
ASTE 404 Mini-Project Library
"""

from .solver import HybridSolver
from .nozzle import NozzleAnalyzer
from .animation import NozzleAnimator
from .utils import load_inputs, load_geometry
from .gas_dynamics import (
    area_mach_relation, 
    normal_shock_relations, 
    solve_expansion_fan, 
    solve_oblique_beta
)

__version__ = "0.3.0"