import os
from aste404_miniproject.utils import load_inputs, load_geometry
from aste404_miniproject.animation import NozzleAnimator

def run_step3():
    print("=== STEP 3: FLIGHT ANIMATION ===")
    
    # Build correct paths relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(project_root, "inputs", "sample_input.txt")
    geo_file = os.path.join(project_root, "inputs", "sample_r_vs_x.csv")
    
    # Verify files exist
    if not os.path.exists(input_file) or not os.path.exists(geo_file):
        print("ERROR: Could not find input files!")
        print(f"Looking for:")
        print(f"  - {input_file}")
        print(f"  - {geo_file}")
        return
    
    # Load files
    print("Loading inputs...")
    inputs = load_inputs(input_file)
    
    print("Loading geometry...")
    geo = load_geometry(geo_file)
    print(f"   > Loaded {len(geo)} geometry points.")
    
    # Initialize the Animator
    print("Initializing animator with standard atmosphere model...")
    animator = NozzleAnimator(inputs, geo)
    
    # Run animation
    print("Starting pre-calculation of 150 altitude frames...")
    animator.run()

if __name__ == "__main__":
    run_step3()