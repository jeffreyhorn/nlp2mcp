#!/usr/bin/env python3
"""
Test script for i++1/i--1 indexing grammar changes.
Tests synthetic examples before running full regression suite.
"""

from src.ir.parser import parse_text

# Test cases from PLAN.md
test_cases = [
    # Baseline (should work before and after)
    ("x(i)", "baseline: simple index"),
    # Circular lead/lag (new feature)
    ("x(i++1)", "circular lead: i++1"),
    ("x(i--2)", "circular lag: i--2"),
    # Linear lead/lag (new feature)
    ("y(i+1)", "linear lead: i+1"),
    ("y(i-3)", "linear lag: i-3"),
    # Multi-dimensional (new feature)
    ("z(i++1, j--2)", "multi-dimensional: i++1, j--2"),
    # Variable offset (new feature)
    ("a(i+j)", "variable offset: i+j"),
]

print("Testing indexing grammar changes...")
print("=" * 60)

passed = 0
failed = 0

for expr, description in test_cases:
    try:
        # Wrap in minimal GAMS context (assignment)
        code = f"Parameter p; p = {expr};"
        tree = parse_text(code)
        print(f"✅ PASS: {description:40s} | {expr}")
        passed += 1
    except Exception as e:
        print(f"❌ FAIL: {description:40s} | {expr}")
        print(f"   Error: {str(e)[:100]}")
        failed += 1

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed")

if failed > 0:
    exit(1)
else:
    print("\n✅ All grammar tests passed!")
    exit(0)
