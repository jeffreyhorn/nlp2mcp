# Analysis — Recovered-Translate Models (ganges family)

**Created:** 2026-04-20
**Sprint:** 25 (Prep Task 5)
**Target models:** `ganges`, `gangesx`, `ferts`, `clearlak`, `turkpow` (the 5 models that recovered translate under doubled timeouts in Sprint 24 Day 13 Addendum, but all hit `path_syntax_error` at the PATH compile step)
**Cross-reference:** [`CATALOG_EMITTER_BACKLOG.md`](CATALOG_EMITTER_BACKLOG.md) (Task 4), [`AUDIT_ALIAS_AD_CARRYFORWARD.md`](AUDIT_ALIAS_AD_CARRYFORWARD.md) (Task 2)

---

## Executive Summary

**All 5 recovered-translate models hit distinct root causes that are NOT covered by the 7 existing Sprint 25 emitter-backlog issues (#1275–#1281) or the #1283 parser non-determinism bug.** Every model failure required a newly-filed issue:

| Model | Compile error | Root cause | New issue | Status |
|---|---|---|---|---|
| `ganges` | 16× Error 66 (undefined parameters) | Emitter strips calibration-from-`.l` assignments | [#1289](https://github.com/jeffreyhorn/nlp2mcp/issues/1289) | Filed |
| `gangesx` | Same as ganges (identical errors) | Same root cause — ganges-family | #1289 | Filed (shared) |
| `ferts` | Error 109 / 108 (identifier too long) | Multiplier names exceed GAMS 63-char limit when synthetic element hashes compound | [#1290](https://github.com/jeffreyhorn/nlp2mcp/issues/1290) | Filed |
| `clearlak` | Error 352 / 149 / 141 (set uninitialized) | Emitter hoists `sum(leaf, ...)` before `leaf(n) = yes$(...)` — dependency-graph bug | [#1291](https://github.com/jeffreyhorn/nlp2mcp/issues/1291) | Filed |
| `turkpow` | Error 98 (line > 80k chars) + cascading | `stat_zt` emitted as a single 144k-char line from `sameas()` Cartesian-product enumeration | [#1292](https://github.com/jeffreyhorn/nlp2mcp/issues/1292) | Filed |

**Unknown 2.6 assumption REVISED.** The prep-time hypothesis that "At least 3 of the 5 are unblocked by some subset of emitter fixes (#1275–#1281)" is **wrong**. The correct statement is: **0 of the 5 are unblocked by existing tracked bugs; all 5 require new issues (#1289–#1292) to be fixed.** Priority 2's leverage on the Solve target (99 → ≥ 105) depends on these 4 new issues landing, not the existing 7.

**Highest-leverage single fix:** #1289 (ganges calibration stripping) unblocks 2 of 5 models (ganges + gangesx). Every other new issue unblocks 1 of 5.

**Fix-minimal subset that unblocks ≥3 of 5:** #1289 + any one of {#1290, #1291, #1292} → 3 models. To unblock all 5, all 4 new issues must land.

**Estimated total Priority 2 additional work (beyond #1275–#1281):** 10–15h for #1289–#1292 combined (4–6h + 2–3h + 3–4h + 1–2h), plus golden-file regression verification on each affected model and the 10 alias-using matching canaries from Task 2.

---

## Section 1 — Per-Model Compile-Error Analysis

Compile-check recipe:

```bash
cd /tmp/task5-compile
gams <model>_mcp.gms action=c lo=2   # action=c = compile only; lo=2 = terse output
cat <model>_mcp.lst | grep -A5 '^\*\*\*\*'
```

### 1.1 `ganges` and `gangesx` (identical errors)

**Result:** 18 errors; `256` solve-statement errors; compile rejected.

```
**** 66  Use of a symbol that has not been defined or assigned
**** 66 equation stat_ax..      symbol "deltax" has no values assigned
**** 66 equation stat_deprec..  symbol "aid"    has no values assigned
**** 66 equation stat_exscale.. symbol "aex"    has no values assigned
**** 66 equation stat_invtot..  symbol "adst"   has no values assigned
**** 66 equation stat_ls..      symbol "as"     has no values assigned
**** 66 equation stat_ls..      symbol "deltas" has no values assigned
**** 66 equation stat_lw..      symbol "av"     has no values assigned
**** 66 equation stat_lw..      symbol "deltav" has no values assigned
**** 66 equation stat_m..       symbol "aq"     has no values assigned
**** 66 equation stat_m..       symbol "deltaq" has no values assigned
**** 66 equation stat_n..       symbol "az"     has no values assigned
**** 66 equation stat_n..       symbol "deltaz" has no values assigned
**** 66 equation stat_nd..      symbol "an"     has no values assigned
**** 66 equation stat_nd..      symbol "deltan" has no values assigned
**** 66 equation stat_nm..      symbol "pnm00"  has no values assigned
**** 66 equation fddef..        symbol "cg"     has no values assigned
```

16 parameter symbols declared but never assigned. In `data/gamslib/raw/ganges.gms`:
- Parameters are **declared** at lines 332–355 with no inline data.
- Parameters are **assigned** at lines 598–602 via calibration expressions that reference solved variable levels (`ls.l(i)`, `s.l(i)`, etc.):
  ```gams
  deltas(i)$ls.l(i) = (k(i)/ls.l(i))**(1/sigmas(i))*pk.l(i)/sum(r$ri(r,i), pls.l(r));
  as(i) = s.l(i)*(deltas(i)*k(i)**(-rhos(i)) + ...)**(1/rhos(i));
  ```

The emitter strips these calibration assignments because they reference `.l` values — post-solve quantities that don't exist at MCP compile time. For the "declare + initial-solve + calibrate + final-solve" pattern this is incorrect: the calibration must run after an initial NLP solve (which `--nlp-presolve` would provide via `$include`).

**Map to tracked bugs:** None. Filed as [#1289](https://github.com/jeffreyhorn/nlp2mcp/issues/1289).

### 1.2 `ferts`

**Result:** many Error 109 (Identifier/Element too long) + Error 108 (Suffix identifier too long); compile rejected.

Example triggering identifier (67 chars, from `/tmp/task5-compile/ferts_mcp.lst:161`):

```
nu_xi_fx_sulf_acid_c8324d9c_kafr_el_zt_4b0342d5_kafr_el_zt_4b0342d5
```

Decomposition:
- `nu_` (3) — multiplier prefix
- `xi_fx_sulf_acid_c8324d9c_` (25) — equation name + 8-char hex hash (the `c8324d9c` suffix)
- `kafr_el_zt_4b0342d5_` (20) — first element with hash
- `kafr_el_zt_4b0342d5` (19) — second element with hash
- **Total: 67 chars > 63 GAMS limit**

The hashes (`c8324d9c`, `4b0342d5`, `876cfd70` also seen) come from the synthetic-element-renaming pass that transforms GAMS-illegal element names (e.g., `kafr-el-zt` with hyphen → `kafr_el_zt_<hash>`). When two such transformed elements are concatenated into a multiplier name, the identifier exceeds the limit.

**Map to tracked bugs:** None. Filed as [#1290](https://github.com/jeffreyhorn/nlp2mcp/issues/1290).

### 1.3 `clearlak`

**Result:** 6 errors; compile rejected.

```
**** 352  Set has not been initialized         (leaf, at line 64)
**** 149  Uncontrolled set entered as constant (tmp1 expression at line 72)
**** 141  Symbol declared but no values have been assigned (ndelta at line 78)
...
**** 257  Solve statement not checked because of previous errors
**** 141  (nlp2mcp_obj_val at line 843, post-solve reference)
```

Generated `data/gamslib/mcp/clearlak_mcp.gms` line ordering:
- **Line 64:** `tmp1 = sum(leaf, nprob(leaf));` ← hoisted too early
- **Line 69:** `leaf(n) = yes$(ord(n) > ...);` ← assignment comes AFTER the sum

Original `data/gamslib/raw/clearlak.gms` line ordering:
- **Line 72:** `leaf(n)$(ord(n) > ...) = yes;` ← assigned
- **Line 95:** `tmp1 = sum {leaf, nprob(leaf)};` ← used after assignment (correct)

The emitter's IR dependency-ordering pass does not model the set-initialization dependency of `sum(leaf, ...)` on `leaf`'s assignment. It hoists the `tmp1 = sum(...)` assignment purely based on data dependencies (`nprob`), forgetting that `leaf` must be populated first.

**Distinct from #1283 (parser non-determinism):** Verified via `PYTHONHASHSEED=0` and `PYTHONHASHSEED=1` regenerations — both produced identical SHA-256 hashes (`d22483…`) for `clearlak_mcp.gms`. The bug is deterministic; it's an emitter statement-ordering bug, not a parser flakiness bug.

**Map to tracked bugs:** None. Filed as [#1291](https://github.com/jeffreyhorn/nlp2mcp/issues/1291).

### 1.4 `turkpow`

**Result:** 18 errors; compile rejected.

```
**** 170  Domain violation for element        (line 43 — parameter data mixed-index)
**** 171  Domain violation for set            (line 196)
**** 98   Non-blank character(s) beyond max input line length (80000) (line 207)
**** 140  Unknown symbol                      (line 207)
**** 8, 37, 409  parse-recovery errors
```

Line 200 of `data/gamslib/mcp/turkpow_mcp.gms` is **144,454 characters long** — nearly double GAMS's 80,000-char input-line limit. Content: the `stat_zt` stationarity equation, emitted as a single line with hundreds of `sameas()` guards joined by `or`:

```gams
stat_zt(m,v,b,t)..
  ((lam_cct(m,v,t)$(vs(t,v)))$(
      sameas(m, 'gas-t') and sameas(v, '1978') and sameas(b, 'high') and sameas(t, '1978')
   or sameas(m, 'gas-t') and sameas(v, '1978') and sameas(b, 'high') and sameas(t, '1983')
   ...  (hundreds more "or sameas(...)" clauses)
   or sameas(m, 'oil')   and sameas(v, '2005') and sameas(b, 'peak') and sameas(t, '2005')
  ) - piL_zt(m,v,b,t))$(mt(m)) =E= 0;
```

This is the alias-aware KKT assembly enumerating every valid `(m, v, b, t)` index combination as an explicit `sameas()` conjunction, concatenating all such conjunctions as disjuncts. The total character count is proportional to the number of valid tuples × the per-tuple text length (~200 chars each). For turkpow's index cardinalities, this produces the 144k-char overflow.

**Map to tracked bugs:** None. Filed as [#1292](https://github.com/jeffreyhorn/nlp2mcp/issues/1292). Not subsumed by Task 2's Pattern A fix — Pattern A addresses the derivative-chain logic, but the overflow is driven by index-set cardinality and the emitter's lack of line wrapping.

---

## Section 2 — Leverage Matrix (Model × Bug)

Rows: the 5 recovered-translate models. Columns: the 7 existing Sprint 25 tracked emitter/stationarity bugs + #1283 + 4 new issues from this task. `✓` means this fix is required to unblock the model; blank means no dependency.

| Model | #1275 | #1276 | #1277 | #1278 | #1279 | #1280 | #1281 | #1283 | **#1289** | **#1290** | **#1291** | **#1292** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ganges`   |  |  |  |  |  |  |  |  | **✓** |  |  |  |
| `gangesx`  |  |  |  |  |  |  |  |  | **✓** |  |  |  |
| `ferts`    |  |  |  |  |  |  |  |  |  | **✓** |  |  |
| `clearlak` |  |  |  |  |  |  |  |  |  |  | **✓** |  |
| `turkpow`  |  |  |  |  |  |  |  |  |  |  |  | **✓** |

**Summary:**

- **Existing tracked bugs (#1275–#1281, #1283): 0 of 5 models unblocked by any of them.** The 7 emitter-backlog issues catalogued in Task 4 address correctness/consistency problems for models that *already* compile. They do not unblock the 5 recovered-translates.
- **New issues #1289–#1292: 5 of 5 unblocked, one per issue (#1289 covers 2 of 5).**

### Leverage ranking

| Rank | Fix | Models unblocked | Notes |
|---|---|---|---|
| 1 | [#1289](https://github.com/jeffreyhorn/nlp2mcp/issues/1289) ganges calibration stripping | 2 (ganges, gangesx) | Highest single-fix leverage |
| 2 (tie) | [#1290](https://github.com/jeffreyhorn/nlp2mcp/issues/1290) ferts identifier length | 1 (ferts) | Smallest effort (2–3h) |
| 2 (tie) | [#1291](https://github.com/jeffreyhorn/nlp2mcp/issues/1291) clearlak statement ordering | 1 (clearlak) | Same dependency-graph area as #1279 |
| 2 (tie) | [#1292](https://github.com/jeffreyhorn/nlp2mcp/issues/1292) turkpow line length | 1 (turkpow) | 1–2h via simple line-wrap |

**Fix-minimal subset to unblock ≥ 3 of 5:** #1289 + one of {#1290, #1291, #1292}. Easiest pair: **#1289 + #1292** (4–6h + 1–2h = 5–8h total).

**Fix-minimal subset to unblock all 5:** all four new issues (#1289 + #1290 + #1291 + #1292). Estimated 10–15h total.

---

## Section 3 — Priority 2 Implications

### 3.1 Revised Priority 2 scope

Task 4's `CATALOG_EMITTER_BACKLOG.md` scoped Priority 2 as 7 issues (#1275–#1281) plus #1283 parser non-determinism, budgeted at 13–18h (baseline). **This task adds 4 new issues (#1289, #1290, #1291, #1292)**, each of which is a prerequisite for any Solve improvement from the recovered-translate set. Revised Priority 2 scope:

| Original (Task 4) | New (Task 5) | Total |
|---|---|---|
| 7 issues + #1283 = 8 issues / 13–18h baseline | +4 issues / 10–15h | **12 issues / 23–33h baseline** |

Even with the contingency-buffer framing from Task 4 (+2h for Batch 3), Priority 2 expands from ~15h to ~25–33h — approximately doubling the original budget.

### 3.2 Revised Solve target math

Sprint 25 Solve target: 99 → ≥ 105 (+6 models). Path to hitting this target:

- **Priority 1 (alias-AD):** expected to recover 2–3 `model_infeasible` → `model_optimal` (camshape, cesam, korcge per Task 2 Unknown 1.7; recovery probability ~40% each → expected value ~1 model).
- **Priority 2 existing (#1275–#1281):** 0 recoveries by themselves (none of the 5 recovered-translates are unblocked).
- **Priority 2 NEW (#1289–#1292):** up to 5 recoveries if all 4 issues land AND each unblocked MCP then compiles cleanly AND PATH solves. Realistic expectation: 2–3 of 5 (some will hit new failure modes post-compile).

**Best case:** 1 (Priority 1) + 5 (Priority 2 new) = +6. **Meets Solve target.**
**Realistic:** 1 (Priority 1) + 2–3 (Priority 2 new) = +3–4. **Just short of target.**
**Worst case:** 0 (Priority 1 P-probability miss) + 1–2 (Priority 2 new) = +1–2. **Misses Solve target.**

**Implication for Sprint 25 execution:** landing #1289 first (2 models' worth of leverage) is the single highest-priority item for hitting the Solve target.

### 3.3 Recommended fix order (revised from Task 4)

Task 4 proposed Batches 1–3 covering #1275–#1281. With #1289–#1292 added:

| Batch | Days | Issues | Effort | Rationale |
|---|---|---|---|---|
| 1 | Day 1–2 | #1275, #1280, **#1292** | 4–7h | Quick emitter wins, no alias-AD coupling; #1292's line-wrap is ~1–2h |
| 2 | Day 3–4 | #1279, #1276, #1281, **#1290** | 8–12h | IR-normalize fix #1279 + emitter-dedup pair (#1276, #1281) + ferts identifier-length fix |
| **2.5** | Day 4 | **#1289** | 4–6h | **High-leverage ganges calibration fix — highest single-fix unblocking (2 models). Land as own PR; keep Day 4 focused** |
| 3 | Day 5–7 (post-Pattern-C) | #1277, #1278, **#1291** | 7–10h | #1291 joins Batch 3 because its fix site (`src/ir/normalize.py` dependency graph) may share code with #1279 (which lands in Batch 2) |

**Total revised Priority 2:** 23–35h. Upper end exceeds the original Task 4 contingency (20h) by ~15h. **Sprint 25 planning decision required:** should Priority 2 expand, or should some of #1289–#1292 be deferred to Sprint 26?

---

## Section 4 — Cross-Reference

### 4.1 To Task 2 (alias-AD)

- Task 2 §Section 5 canary ladder Tier 5 listed `camshape`, `cesam`, `korcge` as infeasibility-adjacent informational targets. None of the 5 recovered-translates overlap with that list.
- #1292 (turkpow sameas line length) is adjacent to Task 2's Pattern A/C work (same `sameas()` guard generation infrastructure) but **not subsumed** — the line-length overflow is driven by index-set cardinality, not the Pattern A bug. Task 2's Pattern A fix may change the clause count (compressing / expanding), but won't fix the overflow.

### 4.2 To Task 3 (parser non-determinism)

- Task 3's corpus survey identified 4 corpus models with multi-row-label tables: `chenery, clearlak, indus, indus89`. `clearlak` is in both that list and this task's recovered-translate list.
- **clearlak's compile errors are NOT caused by #1283.** Verified: the MCP regeneration is byte-deterministic across `PYTHONHASHSEED=0,1` (both produce SHA-256 `d22483…`). The statement-ordering bug (#1291) is the real cause.
- `clearlak` may still be affected by #1283 in the data-loading regions (its `(mar,apr).dry` multi-row-label table could trigger the parser ambiguity), but those data tables don't cascade into the Error 352 on `leaf`. The two bugs are independent.

### 4.3 To Task 4 (emitter backlog)

- Task 4's Batch 2 groups #1279 (robustlp scalar-widening) with other IR-normalize-area fixes. #1291 (clearlak statement ordering) is also in `src/ir/normalize.py`'s dependency graph area. Recommending #1291 joins Batch 2 (or spawns a "Batch 2.5 IR-normalize refactor" if scope warrants it).
- Task 4's `_DeclaredSymbolTracker` helper (proposed in §Section 2.2) doesn't apply to any of #1289–#1292. The new issues are orthogonal to the dedup pattern.

---

## Appendix A — Reproduction Artifacts

All compile-check outputs saved at `/tmp/task5-compile/<model>_mcp.lst` (2026-04-20). Regenerate with:

```bash
mkdir -p /tmp/task5-compile
for m in ganges gangesx ferts clearlak turkpow; do
  cp "data/gamslib/mcp/${m}_mcp.gms" "/tmp/task5-compile/${m}_mcp.gms"
  (cd /tmp/task5-compile && gams "${m}_mcp.gms" action=c lo=2 > /dev/null 2>&1)
done
for m in ganges gangesx ferts clearlak turkpow; do
  echo "=== $m ==="
  grep -nE "^\*\*\*\*" "/tmp/task5-compile/${m}_mcp.lst" | head -10
done
```

## Appendix B — New-Issue Metadata

| # | Title | Labels | Est. Effort |
|---|---|---|---|
| [#1289](https://github.com/jeffreyhorn/nlp2mcp/issues/1289) | Emitter: ganges-family calibration-assignment stripping (ganges, gangesx unblocked) | `sprint-25` | 4–6h |
| [#1290](https://github.com/jeffreyhorn/nlp2mcp/issues/1290) | Emitter: Multiplier naming exceeds GAMS 63-char identifier limit on models with synthetic element hashes (ferts) | `sprint-25` | 2–3h |
| [#1291](https://github.com/jeffreyhorn/nlp2mcp/issues/1291) | Emitter: Statement ordering hoists `tmp1 = sum(leaf, ...)` before `leaf(n) = yes$(...)` assignment (clearlak) | `sprint-25` | 3–4h |
| [#1292](https://github.com/jeffreyhorn/nlp2mcp/issues/1292) | Emitter: stat_zt in turkpow_mcp.gms emits 144k-char line from `sameas()` cross-product (line-length overflow) | `sprint-25` | 1–2h (line wrap) / 4–6h (simplification) |

In-tree issue docs at `docs/issues/ISSUE_1289_*.md` through `ISSUE_1292_*.md`.
