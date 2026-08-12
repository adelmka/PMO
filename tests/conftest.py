import sys
from pathlib import Path

# Add the repository root to the Python path
# This allows tests to import modules from the root (app, models, services)
sys.path.insert(0, str(Path(__file__).parent.parent))
