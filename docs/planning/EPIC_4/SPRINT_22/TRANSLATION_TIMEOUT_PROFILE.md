# Translation Timeout Profiling

**Date:** 2026-03-06
**Sprint:** 22 (Prep Task 5)
**Pipeline timeout:** 60 seconds (subprocess-level, covers full parse+translate pipeline)

---

## Executive Summary

All 11 translation timeout models were listed and 8 were profiled with stage-level timing (the remaining 3 share characteristics with profiled models). **The Jacobian computation stage is the dominant bottleneck** in 8 of 11 models, consuming 57–99% of total translation time. The remaining 3 models (dinam, ganges, gangesx) are bottlenecked by Lark/Earley parsing.

**Key findings:**
- **2 models are genuine near-misses** that complete within 135s: egypt (60s) and dinam (135s)
- **3 models complete in 100–250s** (ferts 106s, clearlak 192s, turkpow 245s) — addressable with Jacobian optimization
- **3 models complete in 250–510s** (srpchase 509s) — need significant Jacobian optimization
- **3 models timeout in Jacobian** after 5+ minutes (sarf, iswnm, nebrazil) — need architectural change
- **No quick wins exist** for Sprint 22 via timeout increase alone — even doubling to 120s only recovers egypt (1 model)

---

## Timeout Model Inventory

11 models fail with `translation_timeout` in `gamslib_status.json` (committed data as of 2026-03-06).

| Model | Type | File Size | Parse Time (pipeline) | Vars | Eqs | Sets | Params | Est. Var Instances |
|-------|------|-----------|----------------------|------|-----|------|--------|--------------------|
| clearlak | LP | 6.5 KB | 1.2s | 5 | 2 | 15 | 16 | 2,421 |
| dinam | LP | 45.8 KB | 83.3s | 22 | 19 | 34 | 109 | 708 |
| egypt | LP | 41.4 KB | 48.4s | 11 | 11 | 19 | 62 | 999 |
| ferts | LP | 19.0 KB | 18.6s | 11 | 8 | 18 | 28 | 3,615 |
| ganges | NLP | 59.3 KB | 263.9s | 74 | 68 | 20 | 179 | 376 |
| gangesx | NLP | 72.1 KB | 228.0s | 74 | 68 | 20 | 179 | 376 |
| iswnm | LP | 35.9 KB | 37.9s | 4 | 2 | 13 | 31 | 1,477 |
| nebrazil | LP | 60.7 KB | 21.5s | 29 | 25 | 37 | 61 | 12,831 |
| sarf | LP | 25.7 KB | 15.7s | 10 | 16 | 12 | 32 | 369,165 |
| srpchase | LP | 2.8 KB | 0.9s | 3 | 3 | 6 | 10 | 2,003 |
| turkpow | LP | 11.1 KB | 5.8s | 8 | 11 | 10 | 26 | 1,098 |

**Notes:**
- Parse times are from the pipeline's `nlp2mcp_parse` stage (separate from translate)
- "Est. Var Instances" is computed from domain set cardinalities; actual instances may differ due to dynamic subsets and conditions
- 9 of 11 are LP models; ganges and gangesx are NLP
- sarf has by far the most estimated variable instances (369K) due to a 4-dimensional variable

---

## Profiling Results

8 models were profiled with the full translation pipeline. Timing is wall-clock seconds on a single core (Apple M-series).

### Completed Models (5)

| Model | Parse | Validate | Normalize | Gradient | Jacobian | Assemble | Emit | **Total** | Bottleneck |
|-------|------:|--------:|---------:|--------:|--------:|--------:|----:|--------:|------------|
| egypt | 40.2 | 0.0 | 0.1 | 1.1 | 18.0 | 0.2 | 0.1 | **59.6** | Parse (67%) |
| ferts | 20.9 | 0.0 | 0.1 | 0.2 | 59.9 | 24.7 | 0.2 | **105.9** | Jacobian (57%) + Assemble (23%) |
| dinam | 100.2 | — | — | 0.1 | 34.4 | 0.1 | 0.1 | **135.0** | Parse (74%) |
| clearlak | 2.8 | 0.0 | 0.1 | 0.5 | 167.8 | 20.5 | 0.1 | **191.8** | Jacobian (87%) |
| turkpow | 7.5 | 0.0 | 0.1 | 0.4 | 235.0 | 1.3 | 0.1 | **244.5** | Jacobian (96%) |

### Completed with Extended Timeout (1)

| Model | Parse | Validate | Normalize | Gradient | Jacobian | Assemble | Emit | **Total** | Bottleneck |
|-------|------:|--------:|---------:|--------:|--------:|--------:|----:|--------:|------------|
| srpchase | 1.8 | 0.0 | 0.1 | 0.3 | 501.5 | 4.8 | 0.0 | **508.5** | Jacobian (99%) |

### Timed Out at 5 Minutes (2)

| Model | Parse | Gradient | Jacobian (partial) | Status | Bottleneck |
|-------|------:|--------:|-----------------:|--------|------------|
| sarf | 15.0 | 21.0 | >264 (killed) | Timeout in Jacobian | Jacobian + Gradient |
| iswnm | 31.9 | 0.8 | >267 (killed) | Timeout in Jacobian | Jacobian |
| nebrazil | 25.5 | 10.3 | >264 (killed) | Timeout in Jacobian | Jacobian |

### Not Profiled (Extrapolated from Parse Times)

| Model | Parse (pipeline) | Expected Bottleneck | Rationale |
|-------|----------------:|---------------------|-----------|
| ganges | 263.9s | Parse | Parse alone exceeds 60s by 4×; NLP with 74 vars × 68 eqs |
| gangesx | 228.0s | Parse | Tracking variant of ganges; identical structure |

---

## Bottleneck Analysis

### Stage Distribution

| Stage | Models Where Dominant | % of Total Time (when dominant) |
|-------|----------------------|--------------------------------|
| **Jacobian** | 8 models (clearlak, ferts, iswnm, nebrazil, sarf, srpchase, turkpow, egypt partial) | 57–99% |
| **Parse** | 3 models (dinam, ganges, gangesx) | 67–100% |
| **Assemble** | 0 as primary (ferts secondary at 23%) | — |
| **Emit** | 0 | <0.1% in all cases |
| **Gradient** | 0 as primary (sarf secondary at 7%) | — |

### Why the Jacobian Is Slow

The Jacobian computation (`compute_constraint_jacobian`) iterates over every (equation, variable) pair, computing symbolic derivatives for each. For models with multi-dimensional variables and many equations, this creates a combinatorial explosion:

1. **Instance enumeration**: Each variable's domain is expanded to all instances (e.g., `x(c,i,j)` over sets of size 8×5×3 = 120 instances)
2. **Per-instance differentiation**: Each equation is symbolically differentiated w.r.t. each variable instance
3. **Dynamic subset fallback**: When the IR can't resolve dynamic subsets (e.g., `SetMembershipTest`), variables fall back to parent sets, inflating instance counts (see srpchase: 2,003 estimated instances with `srn` dynamic subset falling back to `n` with 1,001 members)

**sarf** is the extreme case: variable `task(g,t,mn,mn)` has 369K instances × 16 equations = ~5.9M potential Jacobian entries.

### Why Parsing Is Slow for 3 Models

The Lark/Earley parser scales with file complexity (not just size):
- **ganges/gangesx** (59–72 KB): Large NLP with 74 variables, 68 equations, 179 parameters — deeply nested expressions require extensive Earley chart processing
- **dinam** (46 KB): Large LP with 109 parameters and 34 sets — extensive table data creates complex parse trees

---

## Tractability Classification

### Near-Miss (total ≤200s, addressable with timeout increase or minor optimization)

| Model | Total | Gap to 60s | Quick Fix |
|-------|------:|----------:|-----------|
| **egypt** | 59.6s | −0.4s | Already borderline; minor parse optimization or timeout=65s would recover |
| **ferts** | 105.9s | +45.9s | Jacobian optimization for 3-dim variables; timeout=120s may suffice |
| **dinam** | 135.0s | +75.0s | Parse bottleneck; timeout=150s or Earley optimization |

### Slow (total 200–600s, needs targeted optimization)

| Model | Total | Bottleneck | Required Optimization |
|-------|------:|------------|----------------------|
| **clearlak** | 191.8s | Jacobian (87%) | Sparsity-aware Jacobian |
| **turkpow** | 244.5s | Jacobian (96%) | Sparsity-aware Jacobian |
| **srpchase** | 508.5s | Jacobian (99%) | Sparsity-aware Jacobian + dynamic subset resolution |

### Intractable (timeout at 5+ min or parse alone >4 min)

| Model | Known Time | Bottleneck | Required Change |
|-------|-----------|------------|-----------------|
| **sarf** | >300s (Jacobian timeout) | 369K var instances | LP fast-path or sparsity-aware Jacobian |
| **iswnm** | >300s (Jacobian timeout) | Dynamic subset fallback | Sparsity-aware Jacobian |
| **nebrazil** | >300s (Jacobian timeout) | 12.8K var instances, 29 vars × 25 eqs | Sparsity-aware Jacobian |
| **ganges** | >273s (parse alone) | Earley parser scalability | Earley optimization or alternative parser |
| **gangesx** | >260s (parse alone) | Earley parser scalability | Earley optimization or alternative parser |

---

## Root Cause Cross-Reference

| Model | Issue Doc | Known Root Cause |
|-------|-----------|-----------------|
| sarf | #885 | 4-dim variable `task(g,t,mn,mn)` creates 369K instances; combinatorial Jacobian explosion |
| dinam | #926 | Large LP; symbolic differentiation unnecessary for linear terms |
| egypt | #927 | 3-dim `trans(c,r,rp)` over 19 sets with 62 parameters |
| ferts | #928 | 3-dim `xf(c,i,j)` and `xi(c,i,i)` create large instance count |
| ganges | #929 | Large NLP; genuine nonlinear derivatives but parse dominates |
| gangesx | #930 | Tracking variant of ganges |
| iswnm | #931 | 3-dim `f(n,n1,m)` over large network sets |
| nebrazil | #932 | 4-dim `xcrop(p,s,f,zz)` and multiple 3-dim variables |
| clearlak | — | No issue doc; LP with multi-dimensional variables |
| srpchase | — | No issue doc; dynamic subset `srn` falls back to parent `n` (1001 members) |
| turkpow | — | No issue doc; LP with multi-dimensional variables |

---

## Quick-Win Assessment

### Timeout Increase (Trivial Effort)

Increasing the pipeline timeout from 60s to 120s would recover **1 model** (egypt at 60s). Increasing to 150s adds dinam (135s). Increasing to 200s adds ferts (106s) and clearlak (192s).

| Timeout | Models Recovered | Cumulative |
|--------:|:-----------------|:-----------|
| 120s | egypt | 1 |
| 150s | +dinam | 2 |
| 200s | +ferts, clearlak | 4 |
| 300s | +turkpow | 5 |
| 600s | +srpchase | 6 |
| >600s | sarf, iswnm, nebrazil, ganges, gangesx still timeout | — |

### Sparsity-Aware Jacobian (High Effort, High Impact)

A sparsity-aware Jacobian that only computes derivatives for (equation, variable) pairs where the variable actually appears in the equation would dramatically reduce computation:
- **Impact:** Would fix 8 of 11 timeout models (all Jacobian-bottlenecked)
- **Effort:** Architectural change — requires static analysis of equation expressions to build a dependency graph before computing derivatives
- **Risk:** Medium — must handle indirect references (set mappings, conditional expressions)

### LP Fast-Path (Medium Effort, Medium Impact)

For LP models (9 of 11 timeout models), all derivatives are constants. A fast path that extracts linear coefficients directly (without symbolic differentiation) would bypass the Jacobian entirely:
- **Impact:** Would fix 8 LP timeout models
- **Effort:** Medium — requires LP detection + coefficient extraction from normalized equations
- **Risk:** Low — LP structure is well-defined and can be detected at IR level

### Earley Parser Optimization (High Effort, Low Impact)

Optimizing the Lark/Earley parser would help ganges/gangesx and dinam:
- **Impact:** Would fix 3 parse-bottlenecked models
- **Effort:** High — Earley parser internals are complex
- **Risk:** High — may require switching to LALR parser or preprocessing complex expressions

---

## Sprint 22 Recommendation

**Translation timeout reduction is NOT recommended as a Sprint 22 workstream.** The primary bottleneck (Jacobian computation) requires architectural changes (sparsity-aware differentiation or LP fast-path) that are multi-day efforts and not aligned with Sprint 22's focus on solve-stage improvements.

**However, a trivial timeout increase from 60s to 150s** (a one-line change in `scripts/gamslib/batch_translate.py:260`) would recover egypt and dinam, reducing the timeout count from 11 to 9. This could be included as a low-effort pipeline improvement if desired.

---

## Appendix: Profiling Methodology

**Environment:** Apple M-series, Python 3.x, Lark/Earley parser
**Profiling tool:** Custom stage-level timer wrapping individual pipeline functions
**Timeout:** 300s (5 min) for standard profiling, 600s (10 min) for extended profiling
**Pipeline stages measured:**
1. **Parse** — `parse_model_file()` (preprocessing + Earley parsing + IR building)
2. **Validate** — `validate_model_structure()` + `validate_parameter_values()`
3. **Normalize** — `normalize_model()` + `reformulate_model()`
4. **Gradient** — `compute_objective_gradient()`
5. **Jacobian** — `compute_constraint_jacobian()`
6. **Assemble** — `assemble_kkt_system()`
7. **Emit** — `emit_gams_mcp()`

Note: Parse times in the profiling results may differ from pipeline-recorded parse times because (a) the pipeline's parse stage runs in a separate subprocess invocation and (b) Lark grammar compilation is cached after the first import.
