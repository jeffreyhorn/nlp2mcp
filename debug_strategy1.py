#!/usr/bin/env python3
"""Debug script to trace Strategy 1 objective variable flow."""

from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
from src.kkt.reformulation import reformulate_model
from src.kkt.objective import extract_objective_info

# Compile the test case
gams_file = "tests/fixtures/minmax_research/test1_minimize_min.gms"
print(f"Processing {gams_file}...\n")

# Parse
model_ir = parse_model_file(gams_file)
print("✓ Parsed")

# Normalize
normalize_model(model_ir)
print("✓ Normalized")

print("\n" + "=" * 60)
print("BEFORE STRATEGY 1")
print("=" * 60)
print(f"model_ir.objective.objvar = {model_ir.objective.objvar}")
print(f"model_ir.objective.expr = {model_ir.objective.expr}")

# Check objdef equation
for eq_name, eq_def in model_ir.equations.items():
    if "obj" in eq_name.lower():
        lhs, rhs = eq_def.lhs_rhs
        print(f"\n{eq_name}: {lhs} = {rhs}")

# Reformulate (this includes Strategy 1)
reformulate_model(model_ir)
print("\n✓ Reformulated with Strategy 1\n")

# Check objective after Strategy 1
print("=" * 60)
print("AFTER STRATEGY 1 (from model_ir)")
print("=" * 60)
print(f"model_ir.objective.objvar = {model_ir.objective.objvar}")
print(f"model_ir.objective.expr = {model_ir.objective.expr}")

# Check objdef equation after
print("\nObjective-defining equations after reformulation:")
for eq_name, eq_def in model_ir.equations.items():
    if "obj" in eq_name.lower():
        lhs, rhs = eq_def.lhs_rhs
        print(f"  {eq_name}: {lhs} = {rhs}")

# Check what extract_objective_info returns
print("\n" + "=" * 60)
print("EXTRACTING OBJECTIVE INFO")
print("=" * 60)
obj_info = extract_objective_info(model_ir)
print(f"obj_info.objvar = {obj_info.objvar}")
print(f"obj_info.defining_equation = {obj_info.defining_equation}")

# Verify the defining equation
if obj_info.defining_equation in model_ir.equations:
    eq_def = model_ir.equations[obj_info.defining_equation]
    lhs, rhs = eq_def.lhs_rhs
    print(f"\nDefining equation content:")
    print(f"  {obj_info.defining_equation}: {lhs} = {rhs}")
else:
    print(f"\n*** ERROR: Defining equation '{obj_info.defining_equation}' not found! ***")

# Now check what equation actually DEFINES aux_min_minconstraint_0
print("\n" + "=" * 60)
print("SEARCHING FOR EQUATION THAT DEFINES aux_min_minconstraint_0")
print("=" * 60)

aux_var = "aux_min_minconstraint_0"
found = False
for eq_name, eq_def in model_ir.equations.items():
    lhs, rhs = eq_def.lhs_rhs
    # Check if LHS is aux_var
    if hasattr(lhs, "name") and lhs.name == aux_var:
        print(f"✓ Found: {eq_name}: {lhs} = {rhs}")
        found = True

if not found:
    print(f"*** ERROR: No equation defines {aux_var} on LHS ***")
    print("\nALL equations after reformulation:")
    for eq_name, eq_def in model_ir.equations.items():
        lhs, rhs = eq_def.lhs_rhs
        print(f"  {eq_name}: {lhs} = {rhs}")
