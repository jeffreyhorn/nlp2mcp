# Translation Timeout & Internal Error Investigation — Sprint 24

**Created:** 2026-04-04
**Sprint:** 24 (Prep Task 6)
**Models Investigated:** 7 (6 timeout + 1 internal error)

---

## Executive Summary

6 models timeout at 300s during translation; 1 model (`mine`) has an internal error. The timeout models range from tiny (srpchase: 107 lines, 3 equations) to medium (mexls: 1088 lines, 16 equations), suggesting the bottleneck is not raw model size but specific translation patterns (stochastic programming libraries, complex index interactions, discontinuous functions). The internal error in `mine` is a known `SetMembershipTest` evaluation limitation for dynamic sets.

---

## Timeout Models (6)

| Model | Lines | Equations | Variables | Sets | Params | Aliases | Solve Type |
|---|---|---|---|---|---|---|---|
| gastrans | 242 | 11 | 7 | 7 | 17 | [j] | MINLP |
| iswnm | 691 | 2 | 4 | 13 | 31 | [n1] | LP |
| mexls | 1088 | 16 | 17 | 44 | 49 | [isp] | LP |
| nebrazil | 1021 | 25 | 29 | 37 | 61 | [zp, sp] | LP |
| sarf | 471 | 16 | 10 | 12 | 32 | None | LP |
| srpchase | 107 | 3 | 3 | 6 | 10 | None | LP |

### Bottleneck Classification

| Model | Bottleneck | Pattern | Fixable? |
|---|---|---|---|
| gastrans | MINLP type | `signpower()` discontinuous derivatives | Unlikely — MINLP out of scope |
| iswnm | Normalize/KKT | Multi-dimensional indexed conditions | Investigate — small model |
| mexls | Normalize/KKT | 44 sets, complex indexing | Investigate — may be combinatorial |
| nebrazil | Normalize/KKT | 37 sets, multi-alias | Investigate — similar to mexls |
| sarf | Normalize/KKT | Dense equation structure | Investigate |
| srpchase | Stochastic lib | ScenRed library (DIM=1000) | Unlikely — library expansion |

### Key Observations

1. **No size correlation:** srpchase (107 lines, 3 eqs) and gastrans (242 lines, 11 eqs) timeout despite being small — the bottleneck is translation pattern, not model size.
2. **Parse succeeds for all:** Timeouts are in normalize/KKT assembly, not parsing.
3. **5 of 6 are LP:** LP fast path (Sprint 23 PR #1172) already applied; these still timeout.
4. **4 of 6 use aliases:** Alias interaction may compound with translation complexity.

### Feasibility Assessment

| Model | Sprint 24 Fix Feasibility | Notes |
|---|---|---|
| iswnm | MEDIUM | Small model; profiling may reveal specific bottleneck |
| sarf | MEDIUM | Medium model; worth investigating |
| mexls | LOW | Complex indexing; may need algorithmic improvement |
| nebrazil | LOW | Similar to mexls |
| srpchase | LOW | ScenRed library handling is architectural |
| gastrans | NONE | MINLP out of scope |

**Recommendation:** Investigate iswnm and sarf (smallest/simplest) with detailed profiling. If a common bottleneck pattern is found, it may apply to mexls/nebrazil too.

---

## Internal Error Model (1)

### mine (LP, 73 lines, 2 equations, 4 variables)

**Error:** `SetMembershipTest` evaluation fails for dynamic set `c(l,i,j)`:
```
Set membership for 'c' cannot be evaluated statically because the set has no
concrete members at compile time.
```

**Root Cause:** Set `c` is defined dynamically via:
```gams
c(l,i,j) = yes$((ord(l) + ord(i)) <= card(l) and (ord(l) + ord(j)) <= card(l));
```

The Sprint 23 `SetMembershipTest` evaluation (PR #1198) correctly raises `ConditionEvaluationError` for dynamic sets with no compile-time members. The fallback includes all instances, but the equation domain mismatch (`pr(k,l+1,i,j)` has 4 indices vs `c(l,i,j)` has 3) causes a downstream error.

**Fix Approach:** The equation instance enumeration should handle the domain index count mismatch gracefully when the condition set has fewer dimensions than the equation domain. Estimated fix: 2-3h.

**Fixable in Sprint 24:** YES — small, well-understood issue.

---

## Summary

| Category | Count | Sprint 24 Fixable | Notes |
|---|---|---|---|
| Timeout (investigate) | 2 | Maybe | iswnm, sarf — profile first |
| Timeout (unlikely) | 3 | No | mexls, nebrazil, srpchase — algorithmic |
| Timeout (out of scope) | 1 | No | gastrans — MINLP |
| Internal error | 1 | Yes | mine — SetMembershipTest domain mismatch |

**Best case:** Fix mine + 1-2 timeout models → translate 140 → 142-143 (toward 97% target of 143/147).
