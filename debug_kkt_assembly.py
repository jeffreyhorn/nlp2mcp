#!/usr/bin/env python3
"""Debug KKT assembly to understand the stat_obj issue."""

from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
from src.kkt.reformulation import reformulate_model
from src.ad.gradient import compute_objective_gradient
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.kkt.assemble import assemble_kkt_system
from src.emit.emit_gams import emit_gams_mcp

# Full pipeline
gams_file = "tests/fixtures/minmax_research/test1_minimize_min.gms"
print(f"Processing {gams_file}...\n")

model_ir = parse_model_file(gams_file)
normalize_model(model_ir)

print("=" * 60)
print("BEFORE REFORMULATION")
print("=" * 60)
print(f"Objective variable: {model_ir.objective.objvar}")
print(f"Variables: {list(model_ir.variables.keys())}")

reformulate_model(model_ir)

print("\n" + "=" * 60)
print("AFTER REFORMULATION (Strategy 1)")
print("=" * 60)
print(f"Objective variable: {model_ir.objective.objvar}")
print(f"Variables: {list(model_ir.variables.keys())}")

gradient = compute_objective_gradient(model_ir)
J_eq, J_ineq = compute_constraint_jacobian(model_ir)

print("\n" + "=" * 60)
print("BEFORE KKT ASSEMBLY")
print("=" * 60)
print(f"model_ir.objective.objvar = {model_ir.objective.objvar}")

kkt = assemble_kkt_system(model_ir, gradient, J_eq, J_ineq)

print("\n" + "=" * 60)
print("AFTER KKT ASSEMBLY")
print("=" * 60)
print(f"kkt.model_ir.objective.objvar = {kkt.model_ir.objective.objvar}")

print("\n" + "=" * 60)
print("STATIONARITY EQUATIONS IN KKT")
print("=" * 60)
stat_eqs = list(kkt.stationarity.keys())
for eq_name in sorted(stat_eqs):
    print(f"  {eq_name}")

if "stat_obj" in kkt.stationarity:
    print(
        "\n*** ISSUE: stat_obj exists (obj should NOT have stationarity equation after Strategy 1)"
    )
    print("    But actually, obj is now just a regular variable, so it SHOULD have one!")
    print("    The issue is different than I thought...")
else:
    print("\n? No stat_obj equation")

aux_stat = [eq for eq in stat_eqs if "aux_min" in eq]
if aux_stat:
    print(f"*** ISSUE: {aux_stat[0]} exists")
    print("    aux_min_minconstraint_0 IS the objective variable, should be skipped")
else:
    print("✓ Good: No stationarity for aux_min_minconstraint_0 (it's the objective)")

print("\n" + "=" * 60)
print("GENERATING GAMS MCP")
print("=" * 60)
gams_code = emit_gams_mcp(kkt)
output_file = "/tmp/test1_debug.gms"
with open(output_file, "w") as f:
    f.write(gams_code)
print(f"✓ Generated {output_file}")

# Show the Model definition
print("\n" + "=" * 60)
print("MCP MODEL PAIRS")
print("=" * 60)
for line in gams_code.split("\n"):
    if line.strip().startswith("Model"):
        # Print next 20 lines
        idx = gams_code.split("\n").index(line)
        for i in range(idx, min(idx + 20, len(gams_code.split("\n")))):
            print(gams_code.split("\n")[i])
        break
