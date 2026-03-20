# Catalog: Translate Failures

**Created:** 2026-03-20
**Sprint:** 23 (Priority 5 — translate ≥ 93%)
**Source:** Sprint 23 Prep Task 7
**Pipeline Run:** 2026-03-20 (rerun of all 16 prior translate failures)

---

## 1. Executive Summary

The Sprint 23 prep plan estimated **15 translate failures** (141/156 = 90.4%). After rerunning the pipeline on all prior failures:

- **ferts** and **turkpow** already translate successfully (slow but under timeout)
- **clearlak** recovered on rerun (marginal timeout at 150.0s → now completes in ~148s)
- **Current count: 13 failures** (143/156 = 91.7% translate rate)

Sprint 23 target: ≥ 145/156 (≥ 93%). This requires fixing **2 of 13** failures (not 4 of 15).

### Classification Summary

| Category | Count | Models | Fixability |
|----------|-------|--------|------------|
| **B: Timeout** (≥150s) | 7 | ganges, gangesx, gastrans, iswnm, nebrazil, sarf, srpchase | Mostly intractable without architectural changes |
| **C: Missing IR feature** (LhsConditionalAssign) | 4 | agreste, ampl, cesam, korcge | Fixable — add emitter support for LhsConditionalAssign |
| **D: Internal error** | 2 | mexls, mine | Fixable — specific code fixes needed |

**Key finding:** The 4 LhsConditionalAssign models share a single root cause (missing `expr_to_gams()` handler). Fixing this one handler would recover all 4, exceeding the ≥ 145 target by 4 models (→ 147/156 = 94.2%). The 2 internal errors are also individually fixable. The 7 timeouts are architecturally intractable in Sprint 23.

---

## 2. Detailed Classification

### Category B: Timeout (7 models)

All timeout models hit or exceed the 150-second translation limit (subprocess `communicate(timeout=150)`). The bottleneck is symbolic Jacobian computation in the KKT builder.

| # | Model | Size | Time | Issue | Root Cause | LP? |
|---|-------|------|------|-------|------------|-----|
| 1 | ganges | 59KB, 1175 lines | 150.2s | #929 | Large NLP macro model; multi-dim symbolic Jacobian | No |
| 2 | gangesx | 72KB, 1517 lines | 150.2s | #930 | Sister of ganges; same macro framework | No |
| 3 | gastrans | 8KB, 242 lines | 150.0s | #830 | Dynamic subsets with 0 static members → parent set fallback → 470K Jacobian entries | No |
| 4 | iswnm | 36KB, 691 lines | 150.1s | #931 | 3-dim variable `f(n,n1,m)` over large network sets | **Yes** |
| 5 | nebrazil | 61KB, 1021 lines | 150.1s | #932 | 29 variables; 4-dim `xcrop(p,s,f,zz)` → massive Jacobian | **Yes** |
| 6 | sarf | 26KB, 471 lines | 150.1s | #885 | 4-dim `task(g,t,mn,mn)` → 369K instances → 452M Jacobian entries | **Yes** |
| 7 | srpchase | 3KB, 107 lines | 150.0s | — | Scenario tree construction; dynamic subset expansion | No |

**LP models (3):** iswnm, nebrazil, and sarf are LP models where symbolic NLP→MCP differentiation is unnecessary overhead. A future "LP shortcut" (identity Jacobian, trivial KKT) could bypass the Jacobian entirely, but this is an architectural change beyond Sprint 23 scope.

**gastrans pattern (#830):** Sprint 22 KU-22 confirmed this requires architectural Jacobian changes (sparsity-aware computation or dynamic subset preservation). The dynamic subset fallback creates a combinatorial explosion: 0-member subsets expand to full parent sets, generating ~470K tuples for 7 equations.

**Potential quick win:** srpchase has no filed issue and is small (3KB). It may be a borderline timeout like clearlak was — worth investigating whether a minor optimization would push it under 150s. All others are well over the limit.

#### Timeout Root Cause Summary

The common theme is **combinatorial explosion in symbolic Jacobian computation**:
1. **Large models** (ganges, gangesx, nebrazil): Many variables × many equations × multi-dimensional domains
2. **Dynamic subset fallback** (gastrans): 0-member subsets → parent set expansion
3. **High-dimensional variables** (sarf, iswnm): 4-dim or 3-dim variables with large domain products

Fixing this requires either:
- Sparsity-aware Jacobian (only compute derivatives for variables actually in equations)
- LP shortcut (skip differentiation for LP models)
- Dynamic subset member preservation during parsing

All are **architectural changes** beyond Sprint 23 scope.

---

### Category C: Missing IR Feature — LhsConditionalAssign (4 models)

All 4 models fail with `ValueError: Unknown expression type: LhsConditionalAssign` in `src/emit/expr_to_gams.py`.

| # | Model | Size | Time | Issue | GAMS Pattern |
|---|-------|------|------|-------|-------------|
| 1 | agreste | 13KB, 298 lines | 10.1s | — | `a(p)$sum(s, yield(p,"cotton-h",s)) = 0` |
| 2 | ampl | 2KB, 60 lines | 1.4s | — | `s.up(r,tl)$tl.first = b(r)` |
| 3 | cesam | 26KB, 727 lines | 10.4s | — | `red(ii,jj)$(T0(ii,jj) < 0) = yes` |
| 4 | korcge | 16KB, 427 lines | 7.7s | — | LHS-conditional parameter/set assignment |

#### Root Cause

`LhsConditionalAssign` is an AST node (defined in `src/ir/ast.py:319-342`) representing GAMS LHS-conditional assignments: `param(i)$condition = rhs`. This is semantically distinct from RHS conditionals (`param(i) = rhs$condition`):
- **LHS conditional:** Only updates records where condition is TRUE (others unchanged)
- **RHS conditional:** Assigns 0 where condition is FALSE

The node was introduced in Issue #1015 (shale model fix) and is correctly constructed during parsing. However, `expr_to_gams()` has no case handler for it — when the node reaches the emitter via certain code paths (e.g., computed parameter emission), it falls through to the catchall and raises `ValueError`.

#### Fix Approach

Handle `LhsConditionalAssign` at the **statement/assignment emission layer**, not in `expr_to_gams()`. The LHS-conditional semantics (`lhs$(cond) = rhs`, where false leaves the record unchanged) must be preserved — simply emitting `rhs$cond` would produce RHS-dollar semantics (assigns 0 where false), which is semantically wrong.

The fix should intercept `LhsConditionalAssign` nodes in the assignment emitter (e.g., `original_symbols.py` or `emit_assignments.py`) and emit the condition on the LHS:
```python
# Emit as: lhs$(condition) = rhs;
lhs_str = emit_lhs(node.target, node.indices)
cond_str = expr_to_gams(node.condition, ...)
rhs_str = expr_to_gams(node.rhs, ...)
emit(f"{lhs_str}$({cond_str}) = {rhs_str};")
```

This is consistent with the existing Issue #1015 handling that introduced the `LhsConditionalAssign` node.

**Effort Estimate:** 2-3h (add handler + unit tests for all 4 models)

**Confidence:** HIGH — single root cause, well-defined fix location, all 4 models share it.

---

### Category D: Internal Error (2 models)

| # | Model | Size | Time | Issue | Error |
|---|-------|------|------|-------|-------|
| 1 | mexls | 50KB, 1088 lines | 32.8s | #940 | `Set or alias '*' not found in ModelIR` |
| 2 | mine | 2KB, 73 lines | 2.7s | — | `Unsupported expression type SetMembershipTest in condition` |

#### mexls — Universal Set `'*'` Not Found (#940)

**Error:** `Set or alias '*' not found in ModelIR. Available sets: ['im', 'ir', 'is', ...]`

**Root Cause:** GAMS has a built-in universal set `'*'` containing all labels used anywhere in the model. mexls declares variables/equations over `'*'` (e.g., `Variable x(*)`). The ModelIR has no representation for this universal set. When the KKT builder (`src/ad/index_mapping.py:194`) tries to enumerate instances over `'*'`, the lookup fails.

**Fix Approach:** Add an implicit universal set to ModelIR during parsing — compute the union of all set elements encountered across all sets. Or special-case `'*'` in the index mapping to dynamically compute the universe.

**Effort Estimate:** 3-4h (needs ModelIR change + index_mapping + tests)

**Confidence:** MEDIUM — conceptually straightforward but touches core IR infrastructure.

#### mine — SetMembershipTest Not Supported in Condition Evaluation

**Error:** `Failed to evaluate condition SetMembershipTest(c, (SymbolRef(l), SymbolRef(i), SymbolRef(j))) with indices ('nw', '1', '1', '1'): Unsupported expression type SetMembershipTest in condition.`

**Root Cause:** The equation `pr(k,l+1,i,j)$c(l,i,j)` has a dollar condition using set membership (`$c(l,i,j)`). The `_eval_expr()` function in `src/ir/condition_eval.py` does not handle `SetMembershipTest` nodes. When `enumerate_equation_instances()` tries to evaluate the condition, it catches the exception and issues a UserWarning, then includes the instance by default. Enough warnings accumulate to classify the model as `internal_error`.

**Fix Approach:** Add `SetMembershipTest` evaluation to `src/ir/condition_eval.py`:
1. Import `SetMembershipTest` from `.ast`
2. Add handler: check if the concrete index tuple is a member of the target set's elements in ModelIR
3. Return True/False based on membership

**Effort Estimate:** 2-3h (condition_eval change + tests; related to Issue #1086 harker regression)

**Confidence:** MEDIUM — straightforward addition but `SetMembershipTest` evaluation has edge cases with nested sets and aliases.

---

## 3. Cross-Category Overlap Analysis

None of the 13 translate failure models appear in:
- **path_solve_terminated** (10 models): No overlap
- **model_infeasible** (12 models): No overlap
- **path_syntax_error** (20 models): No overlap

The 13 translate failures are a distinct, non-overlapping category.

**Note:** paperco (#953) and lmp2 (#952) are mentioned in KU-25 as potentially related translate failures. They are NOT translate failures — both translate successfully but fail at the solve stage (paperco → model_infeasible, lmp2 → path_syntax_error). Their loop-body issues (#953, #952) affect MCP output correctness, not translation.

---

## 4. Sprint 23 Priority 5 Target Analysis

**Current:** 143/156 = 91.7%
**Target:** ≥ 145/156 = 93.0%
**Gap:** Need 2 more successes

### Fix Priority Ranking

| Tier | Models | Category | Effort | Impact | Sprint 23? |
|------|--------|----------|--------|--------|------------|
| **1** | agreste, ampl, cesam, korcge | C (LhsConditionalAssign) | 2-3h | **+4 translate** | **YES** — single fix, highest leverage |
| **2** | mine | D (SetMembershipTest eval) | 2-3h | +1 translate | YES — if budget allows |
| **3** | mexls | D (universal set) | 3-4h | +1 translate | MAYBE — touches core IR |
| **4** | srpchase | B (timeout, borderline?) | 1-2h investigate | +0-1 translate | LOW — likely still timeout |
| **5** | ganges, gangesx, gastrans, iswnm, nebrazil, sarf | B (timeout, architectural) | 10-20h+ architectural | +0-6 translate | **NO** — beyond Sprint 23 scope |

### Recommended Sprint 23 Plan

1. **Tier 1 (Days 1-2): Fix LhsConditionalAssign** — 2-3h, recovers 4 models → 147/156 (94.2%)
   - This alone exceeds the ≥ 145 target
   - Single code change in `expr_to_gams.py` or `original_symbols.py`

2. **Tier 2 (if time): Fix mine SetMembershipTest** — 2-3h, recovers 1 model → 148/156 (94.9%)
   - Independent of Tier 1
   - Benefits condition evaluation infrastructure

3. **Tier 3 (stretch): Fix mexls universal set** — 3-4h, recovers 1 model → 149/156 (95.5%)
   - Higher risk (core IR change)
   - Only attempt if Tiers 1-2 succeed and budget remains

**Total effort for target:** 2-3h (Tier 1 alone reaches 147/156)
**Total effort for all fixable:** 7-10h (Tiers 1-3 reach 149/156)

---

## 5. Existing GitHub Issues Cross-Reference

| Model | Issue | Status | Description |
|-------|-------|--------|-------------|
| ganges | #929 | OPEN | Translation timeout (large NLP macro model) |
| gangesx | #930 | OPEN | Translation timeout (ganges variant) |
| gastrans | #830 | OPEN | Jacobian timeout — dynamic subset fallback explosion |
| iswnm | #931 | OPEN | Translation timeout (3-dim network variable) |
| nebrazil | #932 | OPEN | Translation timeout (large LP with 4-dim variables) |
| sarf | #885 | OPEN | Translation timeout — 369K instances, 452M Jacobian entries |
| mexls | #940 | OPEN | Universal set `'*'` not found in ModelIR |
| agreste | — | — | No issue filed (LhsConditionalAssign) |
| ampl | — | — | No issue filed (LhsConditionalAssign) |
| cesam | — | — | No issue filed (LhsConditionalAssign) |
| korcge | — | — | No issue filed (LhsConditionalAssign) |
| mine | — | — | No issue filed (SetMembershipTest eval) |
| srpchase | — | — | No issue filed (timeout, small model) |

**Note:** The 4 LhsConditionalAssign models and mine/srpchase have no filed issues. Consider filing issues for tracking.

---

## 6. Recovered Models (Former Failures)

Three models previously listed as translate failures now succeed:

| Model | Previous Status | Current Status | Note |
|-------|----------------|----------------|------|
| ferts | timeout (150s) | success (115s) | Slow but under limit |
| turkpow | timeout (150s) | success (124s) | Slow but under limit |
| clearlak | timeout (150.0s) | success (~148s) | Marginal — was right at the 150s boundary |

**clearlak** is borderline and may regress to timeout depending on system load. Consider it fragile.

---

## 7. KU Verification Summary

| KU | Status | Finding |
|----|--------|---------|
| KU-22 | ✅ VERIFIED | Internal error fixes (C+D, 6 models) are higher leverage than timeouts (B, 7 models) |
| KU-23 | ✅ VERIFIED | Timeout models follow the gastrans pattern — architectural Jacobian changes needed |
| KU-24 | ❌ REFUTED | Only 2 fixes needed (not 4) — 143/156 baseline, not 141/156. Tier 1 alone (+4) exceeds target |
| KU-25 | ❌ REFUTED | paperco/lmp2 are NOT translate failures; they translate successfully but fail at solve |

---

**Document Created:** 2026-03-20
**Pipeline Run Date:** 2026-03-20
**Next Steps:** File issues for LhsConditionalAssign models; implement Tier 1 fix early in Sprint 23
