#!/bin/bash

echo "=== Running Python Environment Checks ==="

# Run API checks
echo "Running API checks..."
python -m monitor.api_checker

echo ""

# Run Network checks
echo "Running Network checks..."
python -m monitor.network_checker

echo ""

# Run tests
echo "Running PyTest..."
python -m pytest

echo ""
echo "All checks completed."
