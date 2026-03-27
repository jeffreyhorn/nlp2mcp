# Sprint 23 — Issue Fix Opportunities (Prioritized)

**Generated:** 2026-03-27
**Open issues:** 60 in `docs/issues/ISSUE_*.md`
**Goal:** Identify low-hanging fruit for maximum model advancement per hour.

---

## EASY FIX (< 1 hour effort)

High-confidence fixes with clear diagnosis, single-file changes, minimal regression risk.

| Priority | Issue | Model(s) | Problem | Fix Description | Models Unblocked |
|----------|-------|----------|---------|-----------------|------------------|
| **E1** | #894 | srkandw | Parse error — `$libInclude` + quoted element | Quoted `'time-2'` in sum domain treated as set name. Already partially fixed in PR #1153; remaining $125 empty-Sum issue tracked separately. | 1 (partially done) |
| **E2** | #890 | lop | Grammar — `ll(s,s) = no` syntax | Add `#s.#s` subset notation and `= no` assignment to grammar. Single grammar rule addition. | 1 |
| **E3** | #892 | partssupply | Grammar — `Model m / m1 + m2 /` composition | Extend `model_defn` grammar rule for `+`/`-` operators in model definition lists. | 1 |
| **E4** | #896 | turkey | Grammar — parenthesized table column groups | Extend table header parser to expand `(a,b,c)` grouped column headers. | 1 |
| **E5** | #1030 | (internal) | API cleanup — stale `parse_file` entry points | Rename/wrap `parse_file` to `parse_model_file`. Refactor, no model impact. | 0 (code quality) |
| **E6** | #944 | ps5_s_mn | Compilation $141 — multi-solve loop pattern | Strip post-solve comparison code for multi-solve models. Preprocessor fix. | 1 |

---

## MEDIUM FIX (1–3 hour effort)

Well-understood patterns requiring parser/emitter/stationarity changes. Moderate cross-file impact.

| Priority | Issue | Model(s) | Problem | Fix Description | Models Unblocked |
|----------|-------|----------|---------|-----------------|------------------|
| **M1** | #1164 | chenery, shale | $171 domain violation — subset parameters | `_replace_matching_indices` should prefer declared subset domain over superset. Clear diagnosis, 2 files. | **2** |
| **M2** | #918 | qdemo7 | Empty MCP pair — conditional variables | Emit `.fx` for variables whose stationarity is `0=0` due to dollar conditions. Emitter fix. | **1+** (pattern shared by several models) |
| **M3** | #1133 | fawley | SetMembershipTest condition eval failure | Add `SetMembershipTest` support in `condition_eval.py` or fix empty-equation multiplier fixup. | **1+** |
| **M4** | #986 | lands | NA parameter in equation RHS | Detect params with NA values; auto-add `$(param <> na)` conditions in emitter or warn. | **1** |
| **M5** | #939 | maxmin | PATH convergence — division by zero | Same class as #862; domain condition from set-filtered sum not propagated to stationarity. | **1** |
| **M6** | #827 | gtm | $170/$141 compilation errors | Two sub-bugs: skip zero-fill for invalid domain combos + topological sort for computed params. | **1** |
| **M7** | #956 | nonsharp | 37 compilation errors (4 sub-bugs) | Bug A (unquoted elements) is easy; Bug B–D progressively harder. Partial fix unblocks. | **1** |
| **M8** | #1062 | tricp | 760 MCP unmatched variables | Condition `stat_slp`/`stat_sln` on edge set; fix off-edge instances in stationarity builder. | **1** |
| **M9** | #871 | camcge | Division by zero (partially fixed) | Remaining: Jacobian domain index bug `rhot(i)` vs `rhot(it)`. | **1** |
| **M10** | #953 | paperco | $66 — loop-body parameter not emitted | Extract loop-body parameter assignments from `loop(scenario, ...)`. Related to #952. | **1+** |
| **M11** | #940 | mexls | Universal set `'*'` not in ModelIR | Add implicit `'*'` set handling in index_mapping.py. | **1** |
| **M12** | #955 | danwolfe | Parse error — async grid functions | Add 4 grid functions to `FUNCNAME` + `repeat_stmt` grammar rule. | **1** |

---

## LONGER FIX (3–6 hour effort)

Larger scope, multiple interacting systems, or deep architectural changes.

| Priority | Issue | Model(s) | Problem | Fix Description | Models Unblocked |
|----------|-------|----------|---------|-----------------|------------------|
| **L1** | #1137–#1146 | 20+ models | Alias-aware differentiation (#1111 family) | Summation-context tracking in `_diff_varref`/`_partial_collapse_sum`. Single highest-leverage fix. | **~20** |
| **L2** | #926–#933 | 8 models | Translation timeouts (LP/NLP) | LP-specific fast path for symbolic differentiation. Resolves 6 of 8 timeout models. | **6–8** |
| **L3** | #862 | sambal + others | Gradient condition not propagated | Extract gradient conditions from objective sum in AD→stationarity pipeline. Cross-file. | **2–3** |
| **L4** | #882 | camcge | Subset bound complementarity wrong domain | Restrict comp equations to bound subset domain; suppress scalar fix-equations for `.fx` vars. | **1** |
| **L5** | #1041 | cesam2 | Empty MCP pair (66 unmatched) | COLSUM/ROWSUM Jacobian builder not detecting constraint-variable relationship. | **1** |
| **L6** | #952 | lmp2 | Empty dynamic subsets + loop-body | Enhance `_handle_loop_stmt()` for loop-body assignments. Stochastic params complicate. | **1+** |
| **L7** | #1134 | rocket | Dense Jacobian from lag-indexed equations | Lag-domain guard needed in constraint Jacobian for `∂v_eqn(h')/∂g(h)`. | **1** |
| **L8** | #907/#1061 | tforss | NA propagation + KKT + unmatched variable | Loop-before-solve NA param detection + first-iteration value emission. | **1** |
| **L9** | #1162 | camshape | Alias differentiation + boundary guards | Offset substitution partially fixed; higher-order offsets need boundary guards. | **1** |
| **L10** | #945 | launch | Per-instance stationarity dimension mismatch | Consolidate per-instance scalar stats into indexed equations. | **1** |

---

## NOT FIXABLE (Known Limitations)

| Issue | Model | Reason |
|-------|-------|--------|
| #765 | orani | Linearized percentage-change CGE model fundamentally incompatible with NLP→MCP |
| #983 | elec | Strongly non-convex KKT; MCP is structurally correct but PATH can't solve |
| #1070 | prolog | CES fractional exponents cause singular Jacobian at bounds; architectural limitation |

---

## Recommended Fix Order for Maximum Impact

1. **M1 (#1164)** — chenery + shale subset domain fix → **2 models**, 2-3h
2. **L1 (#1111 family)** — alias-aware differentiation → **~20 models**, 4-6h (highest leverage)
3. **L2 (#926–933)** — LP timeout fast path → **6-8 models**, 3-5h
4. **M2 (#918)** — empty stationarity `.fx` → **1+ models**, 1-2h (pattern applies broadly)
5. **E2–E4 (#890, #892, #896)** — grammar fixes → **3 models**, <1h each
6. **M3 (#1133)** — SetMembershipTest condition eval → **1+ models**, 1-2h
7. **M4 (#986)** — NA parameter detection → **1 model**, 1-2h
8. **L3 (#862)** — gradient condition propagation → **2-3 models**, 3-4h
