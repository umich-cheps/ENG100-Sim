"""
This script runs tests with coverage reporting using pytest.
It requires pytest, coverage, and pytest-cov to be installed in your 
Python environment.
"""

import os
import sys
import pytest


# Set PYTHONPATH to the project root (equivalent to setting 
# PYTHONPATH=. in the terminal)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Run pytest with coverage
exit_code = pytest.main([
    '--cov=simu_core',               # package to measure coverage for
    '--cov-branch',                  # enables branch coverage
    '--cov-report=term',             # show report in terminal
    '--cov-report=html',             # also generate HTML report
    'tests/'                         # path to tests
])

if exit_code != 0:
    print(f"Tests failed with exit code {exit_code}")
