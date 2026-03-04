"""
Backwards compatibility module.
The main app is now in backend/main.py
"""

# Re-export from the actual main module
import sys
from pathlib import Path

# Add parent directory to path so we can import from backend/main.py
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app, create_app

__all__ = ['app', 'create_app']
