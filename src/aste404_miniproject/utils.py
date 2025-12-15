import pandas as pd

def load_inputs(filepath: str) -> dict:
    """
    Parses the specific 'Value ! Comment' format of the provided text file.
    """
    # Keys must match the order in Klapsis_Nikitas_input.txt
    keys = [
        "NominalThrust", "Pb1", "Pc", "Tc", "gamma", "MW", 
        "a", "b", "c", "Rwtd", "Rwtu", "Ri", "Ti", "CR"
    ]
    
    values = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if '!' in line:
                # Extract number before the '!'
                val_str = line.split('!')[0].strip()
                values.append(float(val_str))
                
    if len(values) != len(keys):
        print(f"Warning: Expected {len(keys)} inputs, found {len(values)}.")
        
    return dict(zip(keys, values))

def load_geometry(filepath: str) -> pd.DataFrame:
    """
    Loads the geometry CSV, skipping the header.
    """
    # skipping row 1 because your CSV has a text header
    df = pd.read_csv(filepath, skiprows=1, header=None, names=['x', 'r'])
    return df