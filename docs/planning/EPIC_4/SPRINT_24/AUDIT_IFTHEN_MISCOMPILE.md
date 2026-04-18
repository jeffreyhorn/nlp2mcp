# Audit: `$ifThen` / `$elseIf` Miscompilation Blast Radius

**Sprint 24 · Phase 0 of PLAN_FIX_PARTSSUPPLY**

**Question.** Before fixing `_evaluate_if_condition` to recognize
`$ifThen` and `$elseIf` (case-insensitive), which corpus models does
this affect — and is the current wrong-branch behavior masking
success anywhere?

**Method.**
```bash
grep -rln -i '\$ifThen\|\$elseIf' data/gamslib/raw/ | wc -l
```
→ 15 unique models + 1 include file (`pwlfunc.inc`). Cross-referenced
against `data/gamslib/gamslib_status.json`.

---

## Results

| Model | gamslib_type | convexity | translate | solve | Effect after fix |
|---|---|---|---|---|---|
| **partssupply** | NLP | likely_convex | success | failure (path_syntax_error) | **target** — see PLAN_FIX_PARTSSUPPLY |
| **cesam2** | NLP | likely_convex | success | failure (path_solve_terminated) | monitor — may or may not flip |
| gqapsdp | RMIQCP | excluded | — | — | n/a (pipeline_status=skipped) |
| maxcut | MIP | excluded | — | — | n/a |
| circpack | NLP | excluded | — | — | n/a (excluded reason unrelated) |
| epscm | LP | excluded | — | — | n/a |
| sddp, gussgrid, dqq, asyncloop, tgridmix, trnsgrid, spbenders{1,2,4} | LP | error | — | — | out of NLP2MCP scope |

**Only two NLP/convex-gated targets use `$ifThen`/`$elseIf`:
`partssupply` and `cesam2`. Both currently fail solve.** The
remaining 13 hits are either out-of-scope (LP, MIP, MINLP/RMIQCP)
or already excluded by the convexity gate — the preprocessor fix
cannot regress their headline status.

### No "Accidental Success" Cases

No in-scope model is currently recorded as `solve=success` while
using `$ifThen`/`$elseIf`. There is therefore no risk of a "worked
by accident" regression from the fix: every affected in-scope model
is currently failing, so any behavior change is either unchanged or
an improvement.

### Why `partssupply` And `cesam2` Fail Differently

- `partssupply` → `path_syntax_error` (GAMS Error 445 on the
  `icweight(i) = theta(i)$(not 0) + (1 - theta(i) + sqr(theta(i)))$(0)`
  line — the *emitter* Issue 1 bug, not the preprocessor Issue 2
  bug). Preprocessor Issue 2 *also* affects it (wrong `theta` / `p`),
  but the emitter failure is what currently blocks GAMS from
  reaching the solve. Both must be fixed to hit the success criteria.

- `cesam2` → `path_solve_terminated / no_solve_summary` (PATH ran
  but couldn't converge, probably because some `$ifThen` branch
  needed for correct parameter initialization was silently dropped).
  Worth checking after Phase 2 whether the fix alone flips it to
  success.

---

## Conclusion

Proceeding with the fix is safe. Expected deltas:

- `partssupply`: failure → success (primary target).
- `cesam2`: failure → (possible) success (watch in Phase 4).
- No other in-scope model is affected.

The 13 out-of-scope models listed above will see their preprocessor
output change (correct branches taken), but their pipeline status is
driven by the convexity gate, not the translate/solve status, so no
corpus-level metric moves for them.
