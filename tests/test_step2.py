import os
from aste404_miniproject.utils import load_inputs, load_geometry
from aste404_miniproject.nozzle import NozzleAnalyzer

def run_step2():
    print("=== STEP 2: FULL NOZZLE ANALYSIS ===")
    
    # 1. Define Paths to your files
    # Make sure these are in the 'inputs' folder one level up
    input_file = os.path.join(os.path.dirname(__file__), "..", "inputs", "Klapsis_Nikitas_input.txt")
    geo_file = os.path.join(os.path.dirname(__file__), "..", "inputs", "Klapsis_Nikitas_nozzle_geometry.csv")
    
    if not os.path.exists(input_file) or not os.path.exists(geo_file):
        print("ERROR: Could not find input files!")
        print(f"Please ensure '{input_file}' and '{geo_file}' exist.")
        return

    # 2. Load Data
    print("Loading inputs...")
    inputs = load_inputs(input_file)
    print(f"   > Chamber Pressure (Pc): {inputs['Pc']} Pa")
    print(f"   > Gamma: {inputs['gamma']}")
    
    print("Loading geometry...")
    geo = load_geometry(geo_file)
    print(f"   > Loaded {len(geo)} geometry points.")
    
    # 3. Run Analysis
    print("Initializing Analyzer...")
    analyzer = NozzleAnalyzer(inputs, geo)
    
    print("Running Isentropic Solver...")
    analyzer.solve_isentropic()
    
    # 4. Check Results
    print(f"   > Throat Mach: {analyzer.M[analyzer.throat_idx]:.4f} (Should be 1.0)")
    print(f"   > Exit Mach:   {analyzer.M[-1]:.4f}")
    print(f"   > Exit Pressure: {analyzer.P[-1]:.2f} Pa")
    
    # 5. Detect Shock Type
    print("\nDetecting shock configuration...")
    shock_type = analyzer.detect_shock_type()
    
    # 6. Plot Results (with shock overlay if applicable)
    print("\nGenerating Plot...")
    analyzer.plot_results()

if __name__ == "__main__":
    run_step2()