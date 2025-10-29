#!/bin/bash
# Run unit + integration tests
# Expected runtime: < 30 seconds

set -e

echo "Running unit tests..."
pytest tests/unit/ -v --tb=short

echo ""
echo "Running integration tests..."
pytest tests/integration/ -v --tb=short

echo ""
echo "✓ Unit and integration tests passed"
