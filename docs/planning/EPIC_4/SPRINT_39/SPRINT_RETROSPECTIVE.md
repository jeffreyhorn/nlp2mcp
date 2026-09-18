# Sprint 39 — Retrospective

**Closed 2026-09-18 at `bd2af6e9`.** Figures: `SPRINT_LOG.md` §*Day 13*. Every
number below is derived there and quoted here with its commit; none is recalled.

## 1. What the sprint actually did

**Solve 111 · Match 95 · Translate 135 · genuine floor 75 · `path_solve_terminated`
0.** One KPI moved, downward, on purpose: **Match 96 → 95 is a correction** (C2),
and it is the first Match figure in this series that is true. There was **no
upward mover by Day-0 decision** — P4 took branch B, C6 went VOID — and the
sprint's pre-registered claim was that reporting one downward correction and no
gain is the honest shape when the only upward candidate's premise was refuted by
measurement (Task 6: four call sites at 0.5 % of wall-clock). That claim held.

**Three emit landings, all three-gated (C3), all 0-bucket:** dyncge's Pattern-C
B-4 member (partial, remainder named), and two **latent guards** for the
repeated-domain defect class — `#1737` (raises) and `#1741` (declines). **Both
guards were provably unreachable by any corpus model** (186 clean / 0 drift each),
which is precisely why they could land safely, and the survey records why they
deliberately differ.

**The infrastructure landings are the sprint's firmest product.** P7 fixed the
attribution defect behind a spurious match (Remedy A on the retry *branch*, not
one write), renamed a field that asserted a fact its writer could never know, and
shipped schema **3.0.0** with a migration. P8 landed Phase-0 requirements 8a/8b
and the P1/P2 index-repeat gate (**enforced in CI**). P5 surveyed **21** sites,
closed the 4 `NEEDS A GUARD` ones, and pinned the remaining **16** — 5
behaviourally, 11 structurally, the limit stated. P6's consultation follow-up
went out **on its gate date**, breaking a five-sprint slip.

**Prep refuted 63 % of its own unknowns** (11 ✅ / 11 ❌ / 8 🔶 of 30), against
32 % in S38. That is the number to keep: a prep that refutes more of what it
believed is a prep that measured more.

## 2. The thing worth generalising: a claim restated is a claim that will rot

**68 Copilot review rounds across 18 PRs, 26 of them on the four P7/P5 PRs** —
and the four late PRs touched **no `src/` emit path**. Read individually the
findings look like nitpicks: a count beside a list, a rationale beside its
correction, a mirror of a mirror. Read together they are **one defect class in
about ten costumes**, and naming it is the retrospective's job.

**The class: a claim maintained by restatement.** Every instance had the same
anatomy — a fact stated in two places (or twice in one sentence), one of them
updated, the other left standing. The instances, from `#1740`–`#1743`:

| costume | the fact | where it rotted |
|---|---|---|
| count beside list | 4 sites omitted | sentence said 2 |
| count vs identity | 5/11 partition | a swap preserved 5/11 and passed |
| count vs identity | 7/9 verdicts | a swap preserved 7/9 and passed |
| aggregate vs per-item | "some call had distinct concretes" | one shape reached only on the diagonal |
| generic vs specific | `match="repeats"` | any repeated-domain guard would satisfy it |
| function vs nested function | `_substitute_indices` | `_sub_idx` renamed, anchor still matched |
| anchor scope | `if idx not in expr.index_sets` | matched the line *above* the site too |
| raw text vs code | anchor in a comment | deleted site, pin still green |
| figure in the round that changes it | node count 8 → 9 → 10 → 11 | stale **four** times, once after the rule was written down |
| the review artifact | PR description | stale mirror in **six** rounds |

**The durable fix was the same every time: derive, or pin by identity.** The
strength partition became data plus a derived complement; verdict membership
became an exact set; anchors became code-only, function-scoped, nested-aware and
unique-within-scope; the gate figure became commit-pinned and superseded by this
retest. **Not one of those was fixed by remembering harder** — the node count
rotted a fourth time *after* the rule against it was written in the same
document. Writing a rule down is not a mechanism.

**Corollary for the write-up itself:** this sprint's two P7 remedies and two P5
guards each took **one** review round for the code and **five to eight** for the
documentation describing it. The documentation rounds were not wasted — every
finding was correct — but they were *predictable*, and the prediction is the
process change in §7.

## 3. Three findings the KPIs do not carry

**The P5 survey's safety claim was wrong, not incomplete.** It said the
highest-reach sites (`constraint_jacobian`'s `.index()` family, 12/15 models) were
"safe only because of a pass covering one of three sub-shapes". Instrumented on
Day 12: the AD layer **does** reach them with a repeated domain and **computes a
wrong off-diagonal Jacobian**; nothing wrong reaches output because
`emit_gams_mcp` refuses via **#1737**. So the Day-9 guard is load-bearing for a
layer it was never written for. A carried guess would have sent Sprint 40 looking
for a sub-shape pass that does not exist; the survey now says so.

**P10's six models are two classes, and the survey's framing was half right.**
"Manufactured unless the source declares it so" describes Class A (dinam, egypt,
turkpow ×3, nonsharp ×1: positions collapsed, a coordinate lost — tautological
guard or wrong lookup). Class B (gussrisk, nonsharp ×1, shale) is the source's
own declaration reused in *assignment* context, where GAMS reads the diagonal —
a **context** error P2 cannot see from emitted text. **Three of the five
Class-A-effect models have no solve to verify a fix against**, so
property-and-golden is the *primary* verification route for this class.

**The presolve match that was not one.** `weapons`' MCP never produced its own
`MODEL STATUS`; the warm start put the NLP answer in the variables and the
comparison matched itself. Remedy A now gates the retry on the *attribution*
verdict, and `solve_mcp` refuses to claim success for a contradicted status. The
general rule is on record: **a golden can pass structure, DB, NA-guard and
determinism review and still not run** — "the emit actually executes" belongs in
every adoption protocol.

## 4. What went well

- **Day-0 decisions taken and held.** Floor 73 → 75 with provenance; P4 → branch
  B. C6 was voided *before* the sprint ran, not discovered at close.
- **The consultation went out on its date.** Five sprints of slip ended by not
  re-opening the send decision.
- **Every emit change was leak-gated unqualified, alone, four times** — and the
  one contended run this sprint (Day 9) was caught and re-run.
- **Mutation testing caught non-discriminating tests of my own at least six
  times** — a fixture that could not emit, a precondition that returned early, a
  `Sum` with no bound index, a spy never wired, a count asserted against its own
  total, a partition pinned by size. Each looked rigorous and proved nothing
  until the mutant said so.
- **REPLAN exits were used as designed.** lnts was confirmed, implemented,
  verified — and reverted, because the leak gate could not hold it. That is the
  exit working.

## 5. What did not

- **Documentation cost dominated the last four PRs** — 26 review rounds on
  changes touching no emit. §2 names the class; §7 names the fix.
- **The PR description was the stale mirror six times.** No gate checks it, so
  it is corrected only when read — and every time, the reader was the reviewer.
- **Two probes reported passes that could not have failed** — a `python -c` run
  from the repo root (the CWD supplied the package) and a smoke test in a venv
  with an editable install (`src` importable from anywhere). Both were caught,
  both after I had already reported the pass.
- **P10 got no fix.** Correctly, per the disposition — but 11 h of the plan's
  budget went to triage and documentation rather than a landing.
- **One `git stash` popped a stale stash from another branch**, leaving
  `Makefile` in `UU`. Nothing lost; the standing rule (read-only `git show`,
  never stash to switch) was already on record and was not followed.

## 6. The floor, for the record

**75, read from `data/floor_provenance.json` via `floor_tracker.py` at
`bd2af6e9` (C4).** Unchanged across the sprint. The DB's mechanical count is 65
and is not the floor; the tool prints that warning on every run, which is the
S38 P6 measurement-integrity work doing exactly what it was for.

## 7. Process changes to carry into Sprint 40 prep

1. **A figure that changes with the thing it describes is stated once, pinned
   to a commit, and superseded by the next measurement** — never restated per
   round. Applies to node counts, gate figures, partitions, tallies.
2. **Pin by identity, not by count.** A count catches an omission; only an exact
   set catches a permutation. Where a test asserts "N of M", ask what swap
   preserves N.
3. **Anchors are code, scoped, nested-aware, unique.** The test module has the
   resolver; reuse it rather than re-deriving a weaker one.
4. **The PR description is a mirror; regenerate it from the docs at the end
   rather than patching it per round.** Or put a one-line "see SPRINT_LOG
   §Day N" in it and nothing else that can rot.
5. **A probe must be shown able to fail before its pass is believed.** Assert
   the spy fires on a positive control; assert `-S` really hides the package;
   assert the mutant was applied. Two vacuous passes this sprint were reported
   as real.
6. **When a classification changes, sweep on the changed SET** ("which claims
   mention the Class-A models?"), not on the flagged line. Four rounds of #1743
   were downstream sentences quoting a membership that had moved.
7. **Never `git stash` to switch branches.** `git show <ref>:<path>` and
   `--collect-only` are read-only; use them.
