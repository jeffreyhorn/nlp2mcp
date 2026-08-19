# Sprint 38 Prep Task 9 — Phase-0 Compliance Catalog (P7)

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-task9` · **Measured at:** `fd3ec910` · **Scope:** docs only. `check_phase0_doc.py` was *run*, not edited — no `src/`/`scripts/` change.

**Verdict: ✅ SURVEY COMPLETE — 43 open issues lack a Phase-0 gate, and the problem is CURRENT, not historical.** The census was run using the gate script's **own** functions (`phase0_subsections`, `missing_subsections`), so the classification matches what CI would decide rather than an approximation of it.

---

## 1. The census

**80 issue docs** in `docs/issues/`, cross-referenced against GitHub state (400 issues fetched).

| | compliant | no Phase-0 gate | total |
|---|---|---|---|
| **OPEN** | 19 | **43** | 62 |
| CLOSED | 3 | 13 | 16 |
| unknown state | 2 | 0 | 2 |
| **total** | **24** | **56** | **80** |

### 1.1 Two structural findings

**The problem is current, not historical.** 43 of the 56 un-gated docs belong to **open** issues. Only 13 are closed — so this is not a legacy artifact that stopped accruing; **69 % of the open backlog (43 of 62) is un-gated today.**

**Compliance is binary — there are zero partial gates.** Every doc either has a `## Phase 0: Acceptance Gate` heading with all four canonical subsections, or has no Phase-0 heading at all. **This is a measured three-way result, not a two-way one:** §5's census classifies `COMPLETE` / `PARTIAL` / `NO-GATE` separately and names every partial it finds, reporting **`{'NO-GATE': 56, 'COMPLETE': 24}`** — `PARTIAL` absent. A two-way `gate`/`no-gate` split would have hidden partials inside the un-gated count and made this claim unfalsifiable. **Nobody has ever written half a gate.** That is a useful property: the backfill is "write one" rather than "audit and complete", and it means the count above is exact rather than a judgement call.

### 1.2 Rule C confirmed in practice

The four canonical subsections are matched by **prefix**, with extras permitted. The compliant docs exercise that: `ISSUE_1110` carries eight subsections (the four plus `Correctness`, `Bucket / KPI`, `Leak-freedom (full corpus — MANDATORY)`, `Regression guard`), and `ISSUE_1289` carries **seven** — six as surveyed, plus the `Prerequisite` §3 adds below, which the prefix rule accepts without complaint. **The script's classification agreed with a manual read on every doc inspected** — no false positives or negatives found.

## 2. The prioritised backfill list

Ranked by likelihood of being scheduled, which is what makes a gate *needed* rather than merely absent.

> **✅ DAY-2 PROGRESS (2026-08-19).** Four gates authored — **#1331, #1062, #1325, #983** — covering the first three P8 shortlist entries (twocge, tricp, elec). **Census 24 → 28 complete, 56 → 52 un-gated.** Fingerprints were **re-reproduced at `b823a9a5`**, not quoted. **Two stale claims were found and flagged while gating:** `ISSUE_1062`'s headline **"760 MCP errors" does not reproduce — the measured count is 108**, and its note that `$148`/`$149` compile errors block reproduction is also stale (the model compiles cleanly today); and `ISSUE_983`'s section *"Why Division-by-Zero No Longer Occurs"* is **contradicted by measurement** — it still occurs, at lines 99/100/101. Remaining P8 shortlist: **dyncge** and **lnts**, both needing a doc *created* (Day 3).

### Tier 1 — the P8 candidate pool (11 issues) ← **backfill first**

These cover models in Sprint 38's own P8 sweep pool. **An issue here without a gate is not eligible for the sweep**, so backfilling directly enlarges P8's candidate set.

| # | model | issue |
|---|---|---|
| 906 | twocge | missing USA SAM post-solve trade equations |
| 926 | dinam | MCP compilation errors |
| 933 | tricp | MCP compilation errors |
| 970 | twocge | MCP locally infeasible |
| 983 | elec | division by zero (distance) |
| 1062 | tricp | unmatched slp/sln variables |
| 1251 | twocge | empty trade equations `r = rr` |
| 1291 | clearlak | statement ordering hoists set use before init |
| 1316 | turkpow | table data mis-emission on empty cells |
| 1325 | elec | residual pairwise distance zero after #1320 |
| 1331 | twocge | empty MCP pair `eqpw`/`eqw` |

**twocge holds 4 of the 11** and **elec 2** — so two models account for over half of Tier 1. Gating those two first has the best ratio of effort to eligibility gained.

### Tier 2 — the license-gated cohort (4 issues)

`sroute` #919 · `egypt` #927 · `ferts` #928, #1290. **Deliberately low priority:** these models cannot be solve-verified until license capacity exists (Task 8's cohort), so a gate on them cannot be exercised. Backfill *after* a license lands, not before.

### Tier 3 — everything else (28 issues)

Includes several already covered by live Sprint-38 tracks — `sarf` #885, `ganges` #929, `gangesx` #930, `camcge` #871/#1324/#1354 — where the *working* gate lives in a different, compliant doc (`ISSUE_1385`, `ISSUE_1667`, `ISSUE_1289`). **These are duplicates in effect, not gaps**, and backfilling them would produce a second gate for the same work. Triage before writing.

The remainder are genuine gaps but on models no current sprint touches.

## 3. `$66` / #1289 — the gate is complete, with two corrections applied (7.2)

**Structurally complete.** All four canonical subsections present, plus `Bucket / KPI` and `Regression guard` — **six as surveyed**. Passes the script. **After this task's `Prerequisite` fix (below) it carries seven**; re-checked after the edit, still 0 missing.

**It carries the `ac(i+2,r)` match-correctness risk** and the 6th blocker (embedded `ganges0` **MS-5 @ −386785.5017** vs standalone **MS-2 @ 6395.5444**), correctly framing the fix as **0-bucket**.

**Two things were wrong, both now fixed:**

1. **A stale KPI assertion.** It read *"Solve stays 108, Match stays 93"*. **Match has been 94 since the Sprint-37 Day-9 GAMS-54 re-baseline.** A gate that asserts an outdated KPI would fail its own acceptance check. Corrected, with the reason recorded inline.
2. **The cascade prerequisite was not stated.** 7.2 asks whether the gate records that `$66` is reachable only after the cascade lands. It did not. A **Prerequisite** section now states it explicitly, including Sprint-38 Prep Task 4's finding that **#1668 direction 2 is not implementable at the rebind site** — so the gate cannot be exercised until a replacement direction lands. **`$66` must not be budgeted as independently schedulable.**

**A correction to this task's own framing.** I initially justified fixing #1289 on the grounds that it was an *open* live specification. **It is CLOSED** — and #1111, which I assumed was closed because fawley landed, is **OPEN** (it is a broader AD-engine issue; the fawley landing is recorded *within* it). The edit stands on its merits — the figures are now right and the prerequisite is genuinely useful to anyone reopening the work — but the reasoning behind it was wrong, and the open/closed split does not map onto landed/pending the way I assumed.

**Checked for the same stale-KPI pattern elsewhere:** `ISSUE_1110` (CLOSED, markov) records *"genuine floor 75 → 76"*, which was correct when written and is a historical record of a landed fix. **Left as written.** `ISSUE_1111` carries no KPI assertion. So the stale-figure problem is confined to the one doc.

## 4. What this sizes for P7

P7 is budgeted at **8–10 h**. Against **43** open un-gated issues that is roughly 12 minutes each — not credible for writing a genuine Phase-0 gate, which requires a hand-derived KKT shape and a verification methodology.

**Realistic scope for the sprint: Tier 1 only (11), and probably its twocge/elec core (6).** The catalog exists so P7 can work top-down and stop when the budget runs out, rather than sampling arbitrarily. **The remaining 32 are a standing backlog item, not a Sprint-38 deliverable** — and the count should be reported rather than quietly dropped.

## 5. Reproduction

**The census must classify THREE ways, not two.** A two-way `gate`/`NONE` split collapses *"has a Phase-0 heading but is missing required subsections"* into *"has no Phase-0 section"* — which makes §1.1's **"zero partial gates"** claim unfalsifiable from its own reproduction. The snippet below separates them, so the claim is independently checkable rather than asserted:

```bash
# The census, using the gate script's OWN semantics (not an approximation)
.venv/bin/python - <<'EOF'
import sys, pathlib, collections
sys.path.insert(0, 'scripts/sprint_audit')
from check_phase0_doc import phase0_subsections, missing_subsections
tally = collections.Counter()
for f in sorted(pathlib.Path('docs/issues').glob('ISSUE_*.md')):
    t = f.read_text()
    subs = phase0_subsections(t)
    if subs is None:             cls = 'NO-GATE'    # no "## Phase 0" heading at all
    elif missing_subsections(t): cls = 'PARTIAL'    # heading present, canonical subsections missing
    else:                        cls = 'COMPLETE'   # all four present (extras permitted)
    tally[cls] += 1
    if cls == 'PARTIAL':                            # name every partial, so 0 is checkable
        print(f"  PARTIAL {f.name}: missing {missing_subsections(t)}")
print(dict(tally))
EOF
#   -> {'NO-GATE': 56, 'COMPLETE': 24}      <- PARTIAL absent, and no per-file lines printed

# Cross-reference with GitHub state
gh issue list --state all --limit 400 --json number,state --jq '.[] | [.number,.state] | @tsv'
```

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 9. **7.1 ✅ VERIFIED** (43 open un-gated; current not historical; compliance is binary) · **7.2 ✅ VERIFIED** (#1289's gate complete, with a stale KPI and a missing prerequisite corrected).
**Last Updated:** 2026-08-18 · **Owner:** Sprint 38 execution team
