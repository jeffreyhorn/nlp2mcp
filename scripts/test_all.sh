#!/bin/bash
# Run complete test suite
# Expected runtime: < 60 seconds

set -e

echo "Running unit tests..."
pytest tests/unit/ -v --tb=short

echo ""
echo "Running integration tests..."
pytest tests/integration/ -v --tb=short

echo ""
echo "Running e2e tests..."
pytest tests/e2e/ -v --tb=short

echo ""
echo "Running validation tests..."
pytest tests/validation/ -v --tb=short

echo ""
echo "✓ All tests passed!"
