"""
ASTE 404 Mini-Project Library
-----------------------------

A library for 1D Nozzle Flow Analysis (Isentropic & Shocked) 
and Rocket Engine Design/Sizing.
"""

# Expose the main classes to the top level
from .nozzle import NozzleAnalyzer
from .design import EngineDesigner
from .solver import NewtonSolver
from .gas_dynamics import area_mach_relation, normal_shock_relations, standard_atmosphere
from .propellants import get_propellant

# Define version
__version__ = "0.1.0"

# Define what happens when someone types: from aste404_miniproject import *
__all__ = [
    "NozzleAnalyzer",
    "EngineDesigner",
    "NewtonSolver",
    "area_mach_relation", 
    "normal_shock_relations", 
    "standard_atmosphere",
    "get_propellant"
]