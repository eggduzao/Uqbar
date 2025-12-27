#!/bin/bash

# Message
echo "Rendering Acta Diurna Video"

# Argument Template
project_name: str = args[0]
time_each_pic: float = 3.0  | 2        # seconds each image is shown (not counting overlap)
total_duration: float = 300.0  | 04:40 = 260
transition_duration: float = 0.75   # seconds; set 0 for hard cuts
fps: int = 30
width: int = 1920
height: int = 1080

# 2025-12-15-rob-reiner
python -m acta > 



# Completion
echo "Bioldup complete. Results in ${}."
# Cleaning
echo "Cleaning Python build artifacts..."

# Python/System cleanup
find . -name ".DS_Store" -type f -delete
find . -name "._*" -type f -delete
find . -name ".Trashes" -type d -exec rm -rf {} +
rm -rf build/ dist/ *.egg-info/ .eggs/
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*~" -delete
rm -rf .pytest_cache/ .mypy_cache/ .tox/ .coverage .cache/

echo "Cleanup complete."
