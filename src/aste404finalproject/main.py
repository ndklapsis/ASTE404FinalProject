import argparse
import sys
from .utils import load_inputs, load_geometry  # <--- Clean import
from .nozzle import NozzleAnalyzer
from .design import EngineDesigner
from .propellants import get_propellant

def load_inputs(path):
    # Quick parser for the ! delimited file
    d = {}
    keys = ["NominalThrust", "Pb1", "Pc", "Tc", "gamma", "MW", 
            "a", "b", "c", "Rwtd", "Rwtu", "Ri", "Ti", "CR"]
    with open(path) as f:
        vals = [line.split('!')[0].strip() for line in f if '!' in line]
    for k, v in zip(keys, vals): d[k] = float(v)
    return d

def main():
    parser = argparse.ArgumentParser(description="ASTE 404 Nozzle Tool")
    sub = parser.add_subparsers(dest='mode')
    
    # MODE 1: ANALYZE
    p1 = sub.add_parser('analyze', help='Analyze existing nozzle')
    p1.add_argument('--input', required=True)
    p1.add_argument('--geometry', required=True)
    p1.add_argument('--diagnose', action='store_true')
    
    # MODE 2: DESIGN
    p2 = sub.add_parser('design', help='Design new engine')
    p2.add_argument('--thrust', type=float, required=True)
    p2.add_argument('--pc', type=float, default=50.0, help='Bar')
    p2.add_argument('--alt', type=float, default=0.0, help='km')
    p2.add_argument('--time', type=float, default=10.0)
    p2.add_argument('--prop', type=str, default='methalox', 
                    help="Name OR 'gamma,Tc,MW,OF'")

    args = parser.parse_args()
    
    if args.mode == 'analyze':
        inputs = load_inputs(args.input)
        geo = load_geometry(args.geometry) # Uses the util function now
        
        solver = NozzleAnalyzer(inputs, geo)
        solver.solve_with_conditions()
        solver.plot_results()
        if args.diagnose: solver.plot_diagnosis()
        
    elif args.mode == 'design':
        prop = get_propellant(args.prop)
        des = EngineDesigner(args.thrust, args.pc*1e5, args.alt, prop, args.time)
        des.design()

if __name__ == "__main__":
    main()