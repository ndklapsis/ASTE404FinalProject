# Installation & Setup Guide

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, Linux
- **RAM**: 2+ GB
- **Disk**: 500 MB (including dependencies)

---

## Step-by-Step Installation

### Step 1: Clone or Download the Repository

**Option A: Using Git**
```bash
git clone https://github.com/ndklapsis/ASTE404FinalProject.git
cd ASTE404FinalProject
```

**Option B: Download ZIP**
1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to a folder
4. Open terminal/command prompt in that folder

### Step 2: Create a Python Virtual Environment (Recommended)

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux (Bash):**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

**Option A: Install from source (Recommended)**
```bash
pip install -e .
```

**Option B: Manual installation**
```bash
pip install numpy>=1.20.0
pip install pandas>=1.3.0
pip install matplotlib>=3.4.0
```

### Step 4: Verify Installation

```python
python -c "import aste404_miniproject; print(f'Version {aste404_miniproject.__version__} installed successfully!')"
```

You should see:
```
Version 0.3.0 installed successfully!
```

---

## Quick Verification Tests

### Test 1: Import All Modules
```bash
python -c "from aste404_miniproject import *; print('✓ All modules imported')"
```

### Test 2: Run Unit Tests
```bash
python tests/test_step1.py
```

Expected output:
```
=== STEP 1 VERIFICATION ===

[1] Testing Solver on Isentropic Relation...
   Target A/A*=2.0. Calculated Mach: 2.1970
   ✓ Test Passed!

[2] Testing Normal Shock...
   ✓ Normal shock relations verified!
...
```

### Test 3: Test Static Analysis
```bash
cd tests
python test_step2.py
```

This will:
1. Load engine parameters
2. Solve nozzle flow
3. Detect shock type
4. Display comprehensive plots

### Test 4: Test Animation
```bash
python test_step3.py
```

This will:
1. Pre-calculate 150 altitude frames (~20 seconds)
2. Display animated nozzle behavior
3. Show shock evolution during ascent

---

## Environment Setup by Platform

### Windows (PowerShell)

```powershell
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install
pip install -e .

# Verify
python -c "import aste404_miniproject; print('Ready!')"
```

### Windows (Command Prompt)

```cmd
REM Create virtual environment
python -m venv venv

REM Activate
venv\Scripts\activate.bat

REM Install
pip install -e .

REM Verify
python -c "import aste404_miniproject; print('Ready!')"
```

### macOS

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install
pip install -e .

# Verify
python -c "import aste404_miniproject; print('Ready!')"
```

### Linux (Ubuntu/Debian)

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
sudo apt-get install python3-dev libopenblas-dev

# Install package
pip install -e .

# Verify
python -c "import aste404_miniproject; print('Ready!')"
```

### Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install -e .

CMD ["python", "tests/test_step2.py"]
```

Build and run:
```bash
docker build -t aste404 .
docker run -it aste404
```

---

## Conda Installation (Alternative)

If you prefer Conda environment management:

```bash
# Create conda environment
conda create -n aste404 python=3.9

# Activate
conda activate aste404

# Install dependencies
conda install numpy pandas matplotlib

# Install package
pip install -e .
```

---

## Jupyter Notebook Setup

For interactive exploration:

```bash
# Install Jupyter
pip install jupyter jupyterlab

# Start Jupyter Lab
jupyter lab
```

Then create a notebook with:
```python
# Cell 1: Import
from aste404_miniproject import *
import matplotlib.pyplot as plt
%matplotlib inline

# Cell 2: Load data
inputs = load_inputs("inputs/normal_shock_sealevel_input.txt")
geometry = load_geometry("inputs/Klapsis_Nikitas_nozzle_geometry.csv")

# Cell 3: Analyze
analyzer = NozzleAnalyzer(inputs, geometry)
analyzer.solve_isentropic()
shock_type = analyzer.detect_shock_type()
analyzer.plot_results()
```

---

## IDE Configuration

### VS Code

1. **Install Python extension** (Microsoft)
2. **Select interpreter**: Ctrl+Shift+P → "Python: Select Interpreter" → Choose venv
3. **Create `.vscode/settings.json`**:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "editor.formatOnSave": true
}
```

### PyCharm

1. **File** → **Settings** → **Project** → **Python Interpreter**
2. Click gear → **Add** → **Existing Environment**
3. Select `venv/bin/python` (macOS/Linux) or `venv\Scripts\python.exe` (Windows)
4. File → Open → Select project root

### Spyder

```python
# In Spyder console
import sys
sys.path.insert(0, '/path/to/ASTE404FinalProject/src')
from aste404_miniproject import *
```

---

## Troubleshooting Installation

### Issue: "No module named 'aste404_miniproject'"

**Solution 1:** Install in development mode
```bash
cd ASTE404FinalProject
pip install -e .
```

**Solution 2:** Add to Python path
```python
import sys
sys.path.insert(0, '/path/to/ASTE404FinalProject/src')
import aste404_miniproject
```

### Issue: "ModuleNotFoundError: No module named 'numpy'"

```bash
# Reinstall dependencies
pip install --upgrade numpy pandas matplotlib
```

### Issue: "Permission denied" on Linux/Mac

```bash
# Use --user flag
pip install --user -e .

# Or use sudo (not recommended)
sudo pip install -e .
```

### Issue: "ImportError: DLL load failed" (Windows)

```bash
# Reinstall with specific versions
pip install numpy==1.21.0 pandas==1.3.0 matplotlib==3.4.2
```

### Issue: Matplotlib not showing plots

```python
# In Python/Jupyter
import matplotlib.pyplot as plt
plt.ion()  # Enable interactive mode
# OR
%matplotlib inline  # In Jupyter
```

---

## Advanced Configuration

### Custom Python Path

Create `setup.cfg`:
```ini
[metadata]
name = aste404_miniproject
version = 0.3.0

[options]
packages = find:
package_dir =
    = src
python_requires = >=3.8

[options.packages.find]
where = src
```

### Performance Tuning

```python
# Use faster numpy operations
import numpy as np
np.seterr(all='warn')  # Better error messages

# Set number of threads
import os
os.environ['OPENBLAS_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'
```

---

## Uninstallation

### Remove Package

```bash
# Uninstall library
pip uninstall aste404_miniproject

# Remove virtual environment
# Windows:
rmdir /s venv

# macOS/Linux:
rm -rf venv
```

### Clean Installation

```bash
# Remove and reinstall
pip uninstall aste404_miniproject -y
pip install -e . --force-reinstall --no-cache-dir
```

---

## Getting Help

### Check Installation
```bash
python -m pip show aste404_miniproject
```

### Verify Imports
```python
import aste404_miniproject as apm
print(dir(apm))  # List all exported functions
```

### Read Documentation
```python
from aste404_miniproject import NozzleAnalyzer
help(NozzleAnalyzer)  # Interactive help
```

### Run Tests
```bash
python tests/test_step1.py  # Gas dynamics
python tests/test_step2.py  # Static analysis
python tests/test_step3.py  # Animation
```

### Check Logs
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Next Steps

1. **Verify installation:** Run all 4 test files
2. **Explore examples:** Check `/tests/` directory
3. **Read documentation:** Start with QUICKSTART.md
4. **Try it out:** Load your own engine parameters
5. **Contribute:** Submit improvements!

---

**Installation complete! Ready to analyze nozzles! 🚀**

See QUICKSTART.md for your first analysis.
