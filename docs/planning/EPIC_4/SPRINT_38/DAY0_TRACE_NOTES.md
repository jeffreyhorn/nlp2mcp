# Sprint 38 Day 0 — Baseline Re-confirm + GO/NO-GO + the P3 Send

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-day0-baseline` · **Measured at:** `091a6181` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01** · **Scope:** docs/trace only. No `src/`, DB or golden change.

**Verdict: 🟡 CONDITIONAL GO — the sprint starts, but P1 starts as an EVALUATION, not a landing.** Three of four GO/NO-GO conditions hold outright. **Condition (d) fails**, exactly as the prep cycle predicted, and it is reported here rather than worked around.

---

## 1. Baseline — re-derived, not re-read

Recomputed from `data/gamslib/gamslib_status.json` at execution time, keyed on `model_id` (**not** `model_name`, which holds the description). Convex candidates = `convexity.status ∈ {verified_convex, likely_convex}`.

| quantity | S37 close | **derived at `091a6181`** | |
|---|---|---|---|
| convex candidates | 142 | **142** | ✅ |
| Parse | 142 | **142** | ✅ |
| Translate | 135 | **135** | ✅ |
| Solve | 108 | **108** | ✅ |
| Match | 94 | **94** | ✅ |
|   cold-optimal | 65 | **65** | ✅ |
|   presolve | 29 | **29** | ✅ |
| `model_infeasible` | 7 | **7** | ✅ |
| `path_syntax_error` | 6 | **6** | ✅ |
| all-219 Match | 97 | **97** | ✅ |

**Every line reproduces exactly.** No figure on this page was copied from a prep doc; all ten were derived by the block in §6.

### 1.1 The floor — reported as 73, and the mechanical count behaves as predicted

**Genuine floor: 73.** This is the re-baselined figure (owner decision 2026-08-18, PR #1683). Sprints 31–37 recorded **76**, overstated by 3 because the provenance credits three **out-of-corpus `non_convex`** models — `ps2_f_s`, `ps2_s`, `ps3_s_gic`. **P6c owes the historical correction**; until it lands, older docs still read 76.

**The mechanical count returns 65**, exactly as close rule 3 warns. That is not a discrepancy to investigate — it is the known property that **the floor is not DB-derivable**: the *"cold emit byte-identical to pre-fix"* qualifier lives only in the hand-partition. Recorded here so Day 13 does not rediscover it.

## 2. `src/` state — the prep cycle was docs-only, verified

```
git diff 8cffec29..HEAD -- src/    →  EMPTY
git diff 8cffec29..HEAD -- data/   →  EMPTY
```

**Both empty.** Every banked fingerprint therefore reproduces, and the DB is byte-unchanged since the S37 close. The 22 changed files are entirely `docs/` — 14 under `SPRINT_38/`, the rest the cross-doc corrections the prep tasks made in place (`SPRINT_37/`, `SPRINT_36/`, `SPRINT_32/`, `EPIC_5/`, `docs/issues/ISSUE_1289`).

## 3. GO/NO-GO

| # | condition | verdict | evidence |
|---|---|---|---|
| **a** | baseline re-derived and matching the S37 close | ✅ **PASS** | §1 — all ten quantities reproduce |
| **b** | `check-goldens` / `leak-check` working on `main` at scope 163 | ✅ **PASS** | §3.1 |
| **c** | Phase-0 docs present and conforming for every `src/`-touching track | ✅ **PASS** | §3.2 |
| **d** | all unknowns resolved, zero INCOMPLETE | ❌ **FAIL** | §3.3 |

### 3.1 Condition (b) — the gates, and the scope P1's Day-2 gate asserts against

`make check-goldens` → `check_golden_staleness.py`; `make leak-check MODEL=<id>` → the same script with `--expect-drift`. Both invoke cleanly, and **`--min-scope` exists** (the flag P1's Day-2 gate depends on), alongside `--expect-drift`, `--models`, `--json`, `--fix`, `--allow-unverified`.

**Scope reconciles to the expected 163:**

| | |
|---|---|
| `discover_goldens()` | **170** |
| `git ls-files 'data/gamslib/mcp/*.gms'` (the independent source) | **170** |
| allowlisted | **7** — `danwolfe`, `decomp`, `indus`, `nemhaus`, `nonsharp`, `saras`, `trnspwl` |
| **in scope** | **163** ✓ |

**Deliberately not run: the full sweep.** It is ~26 min locally, and Task 6 established the local machine is **~2× the CI runner**, so a local timing here would be misleading rather than informative. Day 2 runs the real gate; Day 0 verifies it is *present and correctly scoped*, which is what condition (b) asks.

### 3.2 Condition (c) — Phase-0 docs for the two `src/`-touching tracks

| track | doc | subsections | missing |
|---|---|---|---|
| **P1 ganges** | `ISSUE_1667_ganges-deferred-bounds-before-include.md` | 6 | none ✅ |
| **P2 sarf** | `ISSUE_1385_sarf-symbolic-emit-o-active.md` | 6 | none ✅ |
| | `ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md` | 4 | none ✅ |

Checked with the CI gate's **own** functions (`phase0_subsections`, `missing_subsections`), not a reimplementation. **#1385 has two conforming docs** — the O(active) one is the live specification for this sprint; the option-1 short-circuit doc is the earlier framing. Day 5 should cite the former.

### 3.3 Condition (d) — FAILS, and this is the sprint's defining fact

**Unknowns 1.1 and 1.3 are Critical and 🔍 INCOMPLETE.** Per the standing rule, *a Critical unknown left INCOMPLETE is a NO-GO condition.*

| # | question | why it is open |
|---|---|---|
| **1.1** | does the four-fix cascade still reach `rc=0` on both models? | contingent on a landable fix; Task 4 proved #1668 **direction 2 unbuildable** |
| **1.3** | does the narrowed predicate pass the full-corpus gate with `prolog` byte-identical? | **there is no predicate to gate** |

**Both are unanswerable by construction.** Each is contingent on a landable fix existing, and Task 4 measured that ganges and `prolog` are **locally indistinguishable at the rebind site** — `bound_indices` **empty for both** — so the predicate the priority rests on has no discriminator to be made of. **No further prep resolves them.** They are not oversights.

**Scoped correctly: this is a NO-GO for P1 as a landing track, not for the sprint.** The other seven priorities depend on neither unknown.

**⇒ P1 enters as an EVALUATION.** Day 1 is a `/tmp` control of **direction C** (#1668 direction 1) whose outcome *is* the answer to 1.1, with 1.3 following on Day 2. **If Day 1 fails, P1 REPLANs to documentation that same day** and ~14 h moves to P8 — not Days 2–3 spent nursing it, which is the pattern that produced Sprint 36's reverted landing attempt.

## 4. P3 — the package is ready; **the send is an OWNER action and is now outstanding**

**Decision made in prep: SEND** (Task 7, channel supplied by the owner 2026-08-18).

**Pre-send checks, all passing:**

| check | result |
|---|---|
| §4 toolchain stamp applied to the attachment | ✅ present — *"Re-confirmed 2026-08-18 under GAMS 54.2.1 / PATH 5.2.01"*, with the original-toolchain caveat on the `INFES`/objective figures |
| attachment unchanged since the stamp landed | ✅ last touched by `f895586b` (the stamp commit itself) |
| attachments exist | ✅ `ROCKET_PATH_CONSULTATION_INPUT.md` (109 lines) · `data/gamslib/raw/rocket.gms` (104 lines) |
| **the failure state still reproduces** | ✅ **rocket, mine and fawley are all `model_infeasible` under GAMS 54.2.1** — the bucket the question describes |
| #1462 has no send record | ✅ **1 comment** (the Sprint-28 bisect), no send record — as Task 7 found |

> ### ⚠ OWNER ACTION REQUIRED — the only thing blocking P3
>
> **Send the §5 message** in `CONSULTATION_DECISION_BRIEF.md` — copy-paste ready, addressed to **`ferris@cs.wisc.edu`**, **`steve@gams.com`**, **`sdirkse@gams.com`** (both Dirkse addresses deliberately; a bounce on one is silent and this is a one-shot message after five carries).
>
> **This session cannot send it** — the claude.ai Gmail connector is unauthenticated and unavailable in a non-interactive session. Authorising it would be done through claude.ai connector settings, but the send is a human action regardless.
>
> **On confirmation, two follow-ups fire** (both agent-executable): post §7's tracking comment to **#1462**, and split `SPRINT_36/CONSULTATION_BUNDLE.md`'s single checkbox into its three real actions.

**Unknown 3.3 stays 🔶 until the send happens** — it asks whether a reply would be actionable, and the answer is pre-registered: a reply counts only if it contains **an option set / `optfile`, a regularization or continuation schedule, or a named reformulation class.** A diagnosis without one of those three does not unblock rocket.

**Follow-up rule:** no reply within one sprint (14 days) ⇒ post a follow-up and treat rocket's +1 as consultation-gated for planning, **without re-opening the send decision**.

## 5. Day 1 hand-off

**Do:** implement **#1668 direction 1** (direction C) as a scratch patch; per model and never inferred across the pair, emit → compile → **read GAMS's own `**** N ERROR(S)` line** → assert `$141`/`$145`/`$149` are 0 and `rc` is 0; then sweep in scratch and confirm nothing outside `{ganges, gangesx, korcge}` is perturbed.

**Do not:** re-attempt direction 2 (refuted — no discriminator exists); count markers with `grep -o '$NNN'` (undercounts **even with no truncation**); touch `src/` on Day 1.

**REPLAN the same day** if `rc=0` is missed on either model or anything outside the expected set moves.

## 6. Reproduction

```bash
# §1 — the baseline, derived (not read from any doc)
.venv/bin/python - <<'EOF'
import json
d=json.load(open('data/gamslib/gamslib_status.json'))
M={m['model_id']:m for m in d['models']}
CONVEX={'verified_convex','likely_convex'}
cand=[m for m in M.values() if (m.get('convexity') or {}).get('status') in CONVEX]
oc=lambda m:(m.get('mcp_solve') or {}).get('outcome_category')
cs=lambda m:(m.get('solution_comparison') or {}).get('comparison_status')
print('candidates', len(cand))
print('Translate ', sum(1 for m in cand if (m.get('nlp2mcp_translate') or {}).get('status')=='success'))
print('Solve     ', sum(1 for m in cand if oc(m) in ('model_optimal','model_optimal_presolve')))
print('Match     ', sum(1 for m in cand if cs(m)=='match'))
print('  cold    ', sum(1 for m in cand if cs(m)=='match' and oc(m)=='model_optimal'))
print('  presolve', sum(1 for m in cand if cs(m)=='match' and oc(m)=='model_optimal_presolve'))
print('mi        ', sum(1 for m in cand if oc(m)=='model_infeasible'))
print('pse       ', sum(1 for m in cand if oc(m)=='path_syntax_error'))
print('all-219   ', sum(1 for m in M.values() if cs(m)=='match'))
EOF

# §2 — docs-only prep cycle
git diff 8cffec29..HEAD -- src/ data/     # both empty

# §3.1 — scope reconciliation, WITHOUT the ~26-min sweep
.venv/bin/python -c "
import sys; sys.path.insert(0,'scripts/sprint_audit')
from check_golden_staleness import discover_goldens; print(len(discover_goldens()))"   # 170
git ls-files 'data/gamslib/mcp/*.gms' | wc -l                                          # 170 (independent)
#   minus the 7 allowlist entries -> 163 in scope

# §3.2 — Phase-0 conformance via the CI gate's OWN functions
.venv/bin/python -c "
import sys, pathlib; sys.path.insert(0,'scripts/sprint_audit')
from check_phase0_doc import phase0_subsections, missing_subsections
for f in sorted(pathlib.Path('docs/issues').glob('ISSUE_16[67]*.md'))+sorted(pathlib.Path('docs/issues').glob('ISSUE_1385*.md')):
    t=f.read_text(); print(f.name, len(phase0_subsections(t) or []), missing_subsections(t))"
```

---

**Document Status:** ✅ Complete — Sprint 38 Day 0. **🟡 CONDITIONAL GO:** (a) ✅ · (b) ✅ · (c) ✅ · **(d) ❌** — two Critical unknowns are unanswerable until Day 1 runs, recorded as a **NO-GO for P1 as a landing track**, not for the sprint. **One owner action outstanding: send the §5 consultation message.**
**Last Updated:** 2026-08-18 · **Owner:** Sprint 38 execution team
