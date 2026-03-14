# Multi-Solve Models Produce Incomparable NLP Reference Objectives

**GitHub Issue:** [#1080](https://github.com/jeffreyhorn/nlp2mcp/issues/1080)
**Status:** OPEN
**Severity:** Medium — Causes false "mismatch" classification for 5 models
**Date:** 2026-03-14
**Affected Models:** senstran, apl1p, apl1pca, aircraft, sparta

---

## Problem Summary

5 Category A (verified_convex mismatch) models have mismatches caused by the pipeline
comparing the MCP objective against an NLP reference from a different solve iteration or
solver mode. These are not KKT formulation bugs — the MCP formulation is correct for the
deterministic/first-solve case, but the NLP reference captures a different problem.

---

## Affected Models

| Model | Issue | NLP Ref Source | MCP Source |
|-------|-------|---------------|------------|
| senstran | Loop modifies `c(ip,jp)` between solves | Last iteration objective | Initial parameter values |
| apl1p | `option lp = decism` (DECIS stochastic) | Stochastic program solution | Deterministic core |
| apl1pca | `option lp = decism` (DECIS stochastic) | Stochastic program solution | Deterministic core |
| aircraft | `y.up` bounds change between 2 solves | 1st solve (tight bounds) | 2nd solve (relaxed bounds) |
| sparta | 4 formulations solved sequentially | Last formulation objective | Last formulation KKT |

---

## Root Cause

The pipeline (`scripts/gamslib/verify_convexity.py`) extracts the **last OBJECTIVE VALUE**
from the GAMS listing file. For multi-solve models, this captures a later solve with modified
parameters/bounds, while the MCP represents a specific (usually last or only) formulation.

For stochastic models (apl1p, apl1pca), the in-model `option lp = decism` overrides the
pipeline's command-line `LP=CPLEX` argument, so DECIS solves the stochastic program rather
than the deterministic LP.

---

## Suggested Fix

1. **Detection**: Scan models for multiple `solve` statements, loops containing solves, or
   stochastic solver options (`decism`, `de`, etc.)
2. **Classification**: Add `multi_solve: true` flag to `gamslib_status.json`
3. **Comparison**: Exclude multi-solve models from match rate calculations, or compare against
   the first/matching solve's objective

---

## Analysis

Full analysis in `docs/planning/EPIC_4/SPRINT_22/CATEGORY_A_DIVERGENCE_ANALYSIS.md`.

Sprint 22 Day 9 WS4 investigation confirmed:
- senstran MCP objective (153.675) exactly equals the well-known deterministic transport
  problem optimum. NLP reference (163.98) is from a later loop iteration.
- apl1p/apl1pca MCP objective (23700.147) is the deterministic core LP optimum. NLP
  references differ because DECIS solves different stochastic scenarios.
- aircraft MCP captures alloc2 (relaxed y.up=+inf). NLP reference is alloc1 (tight y.up).

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `scripts/gamslib/verify_convexity.py:108-182` | NLP objective extraction (last occurrence) |
| `scripts/gamslib/test_solve.py:733-897` | Comparison logic |
| `data/gamslib/gamslib_status.json` | Model status database |
