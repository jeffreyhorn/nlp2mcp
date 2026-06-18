# Objective-gradient re-symbolization collapses a fixed boundary-element reference (`b('%last%')`) to the iterator index

**GitHub Issue:** [#1455](https://github.com/jeffreyhorn/nlp2mcp/issues/1455)
**Status:** **RESOLVED — Sprint 28 Day 9 (2026-06-18), with [#1387](https://github.com/jeffreyhorn/nlp2mcp/issues/1387).** The fixed boundary element `b('%last%')`→`b('s30')` is now preserved verbatim in `stat_fb` (no longer collapsed to `b(j)`), as part of the offset-aware gradient re-symbolization. *(Prior: OPEN — filed Day 8.)*

## RESOLUTION (Sprint 28 Day 9, 2026-06-18)

Fixed within `_resymbolize_offset_gradient` (`src/kkt/stationarity.py`), the dedicated offset-crossterm re-symbolization added for [#1387](https://github.com/jeffreyhorn/nlp2mcp/issues/1387). For the 1-D objective gradient, only the representative column's own element maps to the iterate `j` (and `IndexOffset(col, ±k)` → `j±k`); every OTHER same-set bare concrete element — the `%last%`/`first`/`last` fixed boundary references — is preserved verbatim instead of being mapped to `j` by the generic `_replace_indices_in_expr` (whose declared/equation-domain logic maps every same-set element to the index). cclinpts `stat_fb(j)` now emits `(b('s30') - b(j))$(not last(j))` (literal `b('s30')`) and the `j+1` cross-term `(b('s30') - b(j+1))$(not last(j+1))`, instead of the collapsed `b(j)-b(j)`=0. Gated by `_grad_has_concrete_base_offset` (only fires when the #1387 offset signature is present), so non-offset gradients are unchanged. Verified by the cclinpts integration test + the full-153-golden regen (only cclinpts + chakra change, both → match).
**Severity:** Medium — silently drops an objective-gradient term from a stationarity equation (cclinpts `stat_fb` Term-1).
**Affected models:** cclinpts (confirmed); potentially any model whose objective references a fixed boundary element (`x('first')`, `v('%last%')`, `b(last)`) alongside the iterate.

## Summary

In objective-gradient re-symbolization, a **fixed boundary-element reference** (cclinpts: `b('%last%')` → `b('s30')`, the constant `b(last)`) is wrongly mapped to the stationarity iterator index `j`, because the element is a member of set `j` and is therefore present in `element_to_set`. When the same gradient term also references the iterate (`b(j)`), the two collapse to `b(j) - b(j) = 0` and the term is silently dropped.

## Reproduction (cclinpts, on `main` e9696570)

```python
from src.ir.parser import parse_model_file
from src.ad.gradient import compute_objective_gradient
from src.config import Config
from src.emit.expr_to_gams import expr_to_gams
from src.kkt import stationarity as S
m = parse_model_file("data/gamslib/raw/cclinpts.gms")  # normalize_model not needed for this repro
grad = compute_objective_gradient(m, Config()); im = grad.index_mapping
cid = next(c for c in range(grad.num_cols) if im.col_to_var[c]==("fb",("s1",)))
d = grad.get_derivative(cid)
#   RAW: ((-1) * ((b("s30") - b("s1")) * 1$(not last(j)) + 0.5*(b("s1")-b(s1-1))*1$(not first(j))))
instances = [(c, im.col_to_var[c][1]) for c in range(grad.num_cols) if im.col_to_var[c][0]=="fb"]
e2s = S._build_element_to_set_mapping(m, ("j",), instances)
out = S._replace_indices_in_expr(d, ("j",), e2s, m, equation_domain=("j",))
print(expr_to_gams(out))
#   RE-SYMBOLIZED: ((-1) * ((b(j) - b(j)) * 1$(not last(j)) + 0.5*(b(j)-b(j-1))*1$(not first(j))))
#                            ^^^^^^^^^^^ b('s30')-b('s1') collapsed to b(j)-b(j) = 0
```

Source objective:
```
object.. ObjV =e=    sum(j$(not last(j)),  [b('%last%') - b(j)]*[fb(j) - fb(j-1)])
              +  0.5*sum(j$(not first(j)), [b(j) - b(j-1)]*[fb(j) - fb(j-1)]);
```
`b('%last%')` is the FIXED last-period budget level, not the iterate. The correct re-symbolized `stat_fb(j)` Term-1 is `(b('s30') - b(j))$(not last(j))` — `b('s30')` must stay literal.

## Root cause

`src/kkt/stationarity.py`: `_build_element_to_set_mapping` includes the fixed boundary element (`s30`) in the element→set map (it IS a member of set `j`), and `_replace_indices_in_expr` therefore rewrites `b('s30')` → `b(j)`. There is no distinction between (a) the **iterate** of the equation being built and (b) a **fixed/literal reference** (the `%last%`/`first`/`last` boundary) that must be preserved verbatim.

## Why it is distinct from #1387's offset-anchor fix

#1387's anchor pre-pass rewrites same-set elements as `IndexOffset(base=anchor, offset=ord(e)-ord(anchor))`. Applied here it would turn `b('s30')` into `b(j+29)` (anchor `s1`) — WRONG: `b('%last%')` is a fixed reference, so at an interior `j` (e.g. `s5`) the correct term is `b('s30')-b(j)`, not `b(j+29)` (out of range). The fix must **recognize the fixed boundary element and keep it literal**, not offset it.

## Suggested fix direction

In the objective-gradient re-symbolization path (`_build_indexed_gradient_term`), exclude fixed boundary-element references — the `%last%`/`first(j)`/`last(j)` constant elements that are NOT the differentiated column's own iterate — from the `element_to_set` map (or mark them literal), so they emit as `b('s30')` (or symbolic `b(last)`). Tightly gated to the objective-gradient path; verify no regression for models that legitimately reference such elements.

## Phase 0: Acceptance Gate (to complete alongside #1387 Day 9)

- **Hand-derived shape:** `stat_fb(j)` Term-1 = `(b('s30') - b(j))$(not last(j))` (literal `b('s30')`), present alongside Term-2 `0.5*(b(j)-b(j-1))$(not first(j))` and the #1387 `j+1` cross-terms.
- **Expected emit:** the re-symbolized `b('s30')` stays a quoted literal (or `b(last)`), never `b(j)` or `b(j+k)`.
- **Verification:** per-term grep on `stat_fb(j)` (see ISSUE_1387 §"Verification Methodology"); cclinpts MS 1 rel_diff < 1%; full-corpus byte-stability + re-solve (shared re-symbolization path).
- **PROCEED/REPLAN:** PROCEED if the literal-preservation gate is local to the objective-gradient path and the corpus is byte-stable except cclinpts; REPLAN if preserving the literal regresses models that legitimately re-symbolize boundary elements.

## Related
- [[ISSUE_1387]] — cclinpts `stat_b`/`stat_fb` (the offset cross-term drop + offset-anchor blocker); this is the 4th facet found Day 8, now its own issue.
