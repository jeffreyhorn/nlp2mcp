# Sprint 40 — Carryforwards from Sprint 39

**Filed at Sprint 39 close, 2026-09-18, measured at `bd2af6e9`.** This file is the
entry point Sprint 40's prep looks for **by name** (S33 → S39 unbroken). Each
item carries its **bounded next step**, not its track name, and every figure is
derived in `SPRINT_LOG.md` §*Day 13*.

**Sprint 39 closed at Solve 111 · Match 95 · Translate 135 · floor 75 ·
`path_solve_terminated` 0.** Nothing below is a regression; three items are
0-bucket by design and are carried because they are *named work*, not because
they failed.

---

## 1. P10 — the six P2-flagged models, triaged into TWO classes (0 bucket)

`P2_VIOLATION_TRIAGE.md` is the work list. The ratchet stands at **9 = baseline
9**; no fix landed because none could be demonstrated correct on three of the
affected models.

| class | models | root | effect | next step |
|---|---|---|---|---|
| **A — MANUFACTURED** | dinam, egypt, turkpow ×3, **nonsharp ×1** | the source keeps two positions distinct; emit substitutes one symbol into both | a coordinate is lost — tautological guard (`ord(x) > ord(x)`) or wrong lookup (egypt's `tranc(rp,rp)`) | **turkpow first** — the alias-minting site is named (`t__kkt1` into both coordinates of `vs(t,v)`); each fix needs its own Phase-0 doc + golden regen |
| **B — DECLARATION-faithful, ASSIGNMENT-narrowing** | gussrisk, **nonsharp ×1**, shale (B origin, A effect) | the source *declares* a symbol (set OR parameter) over the same set twice — legal, the full product — and emit reuses that domain in assignment/guard context, where GAMS reads the **diagonal** | statement covers only the diagonal | needs the declaration-vs-assignment context distinction, which the emitted text alone does not carry — a larger change |

⚠ **Three of the five Class-A-effect models have NO solve to verify a fix
against:** egypt and shale are license-gated; **nonsharp is convexity-excluded
with no `mcp_solve` record at all.** Property-and-golden verification is the
*primary* route for this class, not a fallback. The **four** Class-A-effect
**models** with a record — **dinam, egypt, shale, turkpow** (models, not
fingerprints; turkpow's ×3 in the table is three fingerprints in one model) — are
all `mcp_solve: failure` today for other reasons, measured from the DB, so no fix
here moves a reported figure. Plan it as correctness work, not KPI work.

⚠ **nonsharp has one reference of EACH class.** A Class-B fix leaves its Class-A
reference untouched. Do not treat the model as one item.

## 2. P3 lnts — mechanism BANKED, not landed

Days 4–5. The hypothesis (`fix_rhs = "0"` fallback) was **confirmed at runtime**;
the fix was written, verified, and **reverted** because it touched a live-match
model's emit path without a fail-before the leak gate could hold. Next step:
**author the Phase-0 gate first, with the fail-before, then re-apply the banked
diff.** The diff is in the Day-5 log; do not re-derive it.

## 3. P4 sarf — attribution done, implementation not started (branch B)

Days 7–8. `_diff_sum` is **2.9 % self / 7.5 % inclusive**; **70.9 %** of
wall-clock is in `compute_constraint_jacobian`; `gradient.py:453` is dead. The
Phase-0 gate is authored. Next step: **the O(active) re-arch at the Jacobian,
20–28 h** (S37 carry) — not the four `_diff_sum` call sites, which Task 6 measured
at 0.5 %. C6 will apply only if a branch-A track starts.

## 4. NEW — #1737 is load-bearing for the AD layer, and the survey's safety claim was wrong

`POSITIONAL_DOMAIN_SURVEY.md` §3 (superseded note) and
`tests/unit/kkt/test_positional_domain_sites.py::test_the_AD_collapse_is_reachable_but_EMIT_refuses_it`.

The survey said the highest-reach `.index()` sites were *"safe only because of a
pass covering one of three sub-shapes"*. Measured: `_substitute_indices` **is**
reached with a repeated domain (12 calls for a `rep(i,i)` model) and computes a
**wrong off-diagonal Jacobian**; nothing wrong escapes only because
`emit_gams_mcp`'s `detect_empty_equation_instances` refuses via **#1737**.
Next step: **none required** — the test pins the specific refusal by the
detector's own context string. Carried so that **nobody narrows #1737** without
knowing four other sites depend on it.

## 5. NEW — a pre-existing diagonal-reference defect (needs its own issue)

Found while instrumenting #1741: a model with `diagsum(j).. sum(i, tsam(i,i))`
emits `stat_tsam(i,j).. 1 =E= 0;` — the multiplier term appears **dropped**.
B-3 is called 0× for it, so this is unrelated to the Sprint-39 guards and is on
`main`. Next step: **open the issue, write the Phase-0 doc** (layer: probably
`_diff_sum`'s diagonal handling, but trace before naming — three of four S38
gates named the wrong layer).

## 6. NEW — the 11 structurally-pinned P5 sites, and the two with no discriminating input

`test_positional_domain_sites.py` pins 16 sites: **5 behaviourally, 11
structurally** (anchor text asserted in live code, nothing executed). A guard at
a structural-only site could keep its anchor while its logic is broken. A
nine-shape probe of `_match_subset_domain` and `_compute_index_offset_key` with
the consume-once guards **disabled** produced byte-identical results every time.
Next step: **find an input that discriminates those two** — or record that none
exists at 2-D and the guards are dead code, which is a different finding.

## 7. Smaller items, each with its next step

| item | where | next step |
|---|---|---|
| `scripts/integration_health_check.py` fails from an uninstalled checkout (six module-level `src` imports, no `sys.path` bootstrap) | pre-existing on `main` | two-line bootstrap, as in `run_full_test.py:65` |
| the 7 `model_infeasible` models compare as `skipped`/`compare_mcp_failed` where `mismatch` is arguably more honest (NLP optimal, our MCP infeasible) | `compare_solutions`, Case 6 | **KPI-visible** — needs a Phase-0 doc; do not fold into a review fix |
| `kpi_block`'s dict key `all_219_match` hardcodes 219 | `kpi_block.py` | cosmetic now that the checker's label derives from the cited population |
| `ISSUE_933_tricp-mcp-compilation-errors.md` | still OPEN and untriaged | triage or close |
| **the license-gated cohort of 11** | `path_solve_license` | ceiling +11 Solve; excluded from projections, **not written off**; re-test as ONE batch when a license is available |

## 8. Standing process findings — carry these into Sprint 40's prep

From `SPRINT_RETROSPECTIVE.md` §7, restated here because prep reads this file
first:

1. **A figure that changes with the thing it describes is stated once,
   commit-pinned, and superseded by the next measurement** — never restated per
   review round. The node count rotted **four** times this sprint, once after
   the rule was written down.
2. **Pin by identity, not by count** — a count catches an omission; only an
   exact set catches a permutation.
3. **A probe must be shown able to fail before its pass is believed** — two
   vacuous passes were reported as real this sprint.
4. **The PR description is a mirror; regenerate it from the docs at the end** —
   it was the stale mirror in six rounds of one PR.
5. **When a classification changes, sweep on the changed SET, not the flagged
   line.**
6. **Never `git stash` to switch branches** — `git show <ref>:<path>` is read-only.
7. **The leak gate runs ALONE** — contention narrows its scope silently; this
   sprint hit it once and caught it.

## 9. Banked, not started — rejected candidates stay rejected

- **camcge** → Epic 5 (drop-row BANNED).
- **ganges** → the **`$149` rebind site** is closed (#1668, both directions
  closed on measurement, S38). ⚠ **ganges itself is NOT closed** (PR #1744
  review — an earlier revision said "closed", which would let this file drop
  it): **#1667** (deferred `.l`-dependent bounds emitted before the presolve
  `$include`), **#929/#930** (ganges/gangesx translation timeout) are **OPEN**,
  and the 6th blocker — the embedded-NLP-diverges class (#1378/#1424) — has **no
  issue of its own**. Sprint 40 prep should file that one.
- **rocket / mine** → consultation sent 2026-08-26, follow-up posted 2026-09-09
  (#1462 / #1443). **Do not re-open the send decision.**
- **agreste / cesam / indus** → banked, new diagnosis required.
- **P2 dyncge B-4 — the `eqII` remainder** → handed back to #1381 (Day 3). ⚠ An earlier revision labelled this "P4 lnts", which is wrong twice over: lnts is P3 (§2 above), and `eqII` belongs to the dyncge partial, not to lnts (PR #1744 review).
