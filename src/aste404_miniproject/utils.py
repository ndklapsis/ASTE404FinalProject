import pandas as pd
import os

def load_inputs(filepath: str) -> dict:
    """
    Reads the ASTE475-style input text file.
    Format: 'Value ! Comment'
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    # These keys match the order in your Klapsis_Nikitas_input.txt file
    keys = [
        "NominalThrust", "Pb1", "Pc", "Tc", "gamma", "MW", 
        "a", "b", "c", "Rwtd", "Rwtu", "Ri", "Ti", "CR"
    ]
    
    values = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue # Skip empty lines
            
            # Split at the '!' comment marker
            if '!' in line:
                val_str = line.split('!')[0].strip()
                try:
                    values.append(float(val_str))
                except ValueError:
                    pass # Skip lines that don't start with a number

    # Basic error checking
    if len(values) < len(keys):
        print(f"Warning: Expected {len(keys)} inputs, found {len(values)}.")
    
    # Zip them into a dictionary for easy access (e.g., inputs['Pc'])
    return dict(zip(keys, values))

def load_geometry(filepath: str) -> pd.DataFrame:
    """
    Reads the geometry CSV file.
    Assumes header is on row 0.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Geometry file not found: {filepath}")

    # Load using pandas for speed and reliability
    # forcing column names ensures code works even if CSV header changes slightly
    df = pd.read_csv(filepath, header=0, names=['x', 'r'])
    return df