#!/bin/bash
# Run fast unit tests only
# Expected runtime: < 10 seconds

set -e

echo "Running unit tests..."
pytest tests/unit/ -v --tb=short

echo ""
echo "✓ Unit tests passed"
