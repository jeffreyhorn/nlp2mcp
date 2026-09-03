# Sprint 39 — Per-Day Execution Prompts

**Written by** Prep Task 12 · **2026-09-02** · companion to `../PLAN.md`

**Every day:** branch `planning/sprint39-dayN-<slug>` from `main` → work → **quality gate only if `*.py` changed** (`make typecheck && make format && make lint && make test`) → commit → push → PR → wait for review → reply to each comment on its own thread. **Docs/DB/golden-only PRs skip the gate.**

**Every day — two checkpoints, because the PR body does not exist until the PR does.**

*Before pushing:*

```bash
make check-doc-figures
git log -1 --format=%B | grep -c "Co-Authored-By\|Generated with"    # must print 0
```

*Before creating the PR* — write the body to a file first, so it can be checked before it is sent:

```bash
grep -c "Co-Authored-By\|Generated with" /tmp/pr-body.md            # must print 0
gh pr create --base main --head <branch> --title "<title>" --body-file /tmp/pr-body.md
```

⚠ **`grep -c` exits 1 when the count is 0**, so do not chain either line with `&&` — read the printed number. A `&&` chain here fails on the *good* case.

**⚠ Derive every figure at execution time.** Close rule **C5**. `kpi_block.py` carries its commit and warns on a dirty DB; `floor_tracker.py` reads the provenance file — the mechanical DB count yields **65** and looks authoritative.

---

## Day 0 (2026-09-03) — P1: the floor decision · 6 h

Branch `planning/sprint39-day0-floor`. **This is a decision, and it blocks the sprint's own baseline.**

Read `FLOOR_DECISION_BRIEF.md`. It does **not** decide — it assembles the evidence, refutes the plan's case for 73 (`polygon`, the named in-corpus precedent, is `likely_convex` exactly like twocge and elec), and makes **74** live via a distinction the plan did not anticipate.

**Deliverables:** the decision recorded in `SPRINT_LOG.md`; if 74 or 75, append to `data/floor_provenance.json` **and update `expected_floor` in the same change** (the tracker exits non-zero on divergence) plus the four downstream sites the brief names. Re-derive the baseline at the settled floor.

**⚠ Also decide P4's branch today** (`PLAN.md` §3) — A keep-as-scoped, B re-scope, or C defer. Day 7 opens on **A** by default.

**Gate:** `floor_tracker.py` agrees with the recorded decision; `make check-doc-figures` clean.

## Days 1–3 (09-04 … 09-06) — P2: dyncge · 20 h · + P8 8a/8b · 8 h

Branch `planning/sprint39-day1-dyncge` (and `-day2`, `-day3`).

`ISSUE_1714` has the full Phase-0 gate. **Day 1's first job is to confirm the layer by trace, not to implement** — three of four Sprint-38 gates named the wrong layer, and this one is `src/kkt/stationarity.py` ~7107–7131, the #1081 dim-mismatch branch.

**The controls are pre-registered:** `stat_pq` is correct and must stay **byte-identical**; the residual must reach **`CASE_A`**; the leak gate must drift **dyncge alone**.

**⚠ Do not write new emit logic before checking whether it exists for another population** (P8's 8b, and the lesson dyncge itself produced).

**REPLAN exits:** `PLAN.md` §3.

**P8 alongside:** Day 2 lands **8a** (the layer field + the **added-only** assertion — `pulls.listFiles` already returns `status`; the workflow discards it). Day 3 lands **8b** (the Phase-0 template's *nearest existing mechanism* field). **Both need a fail-before test**; 8a's negative control is that a `modified` doc without a Layer line still **passes**.

## Days 4–5 (09-07, 09-08) — P3: lnts · 18 h · + Checkpoint 1

Branch `planning/sprint39-day4-lnts`.

`LNTS_PROBE_DESIGN.md` fixes the confirm/refute criteria **before** the probe runs — honour that ordering. The collision is confirmed at runtime, and **the banked fix surface is refuted**: `fix_rhs = "0"` at `emit_gams.py:3060–61` **never runs**; the real blanket is **`:3121`**. The machinery to fix it exists — `_fx_eq_name()` at `:711`, the `suppressed` set at `:920`.

**⚠ `cesam` must NOT be batched with lnts.** Same MS-4-at-iteration-0 signature, **0 `_fx_` equations** — a shared signature is not a shared mechanism.

**Day 5 ends with Checkpoint 1:** `--resolve-changed --since-commit 9ab2c0c3`. **NO-GO on any `backward` or `missing` row.**

## Day 6 (2026-09-09) — P6: the date gate · 6 h · + P8 8c/8d · 4 h

Branch `planning/sprint39-day6-consultation`.

**⏰ This day cannot move.** Re-read `CONSULTATION_FOLLOWUP_PACKAGE.md` §1 first — it is the only section that goes stale, and it was written 2026-09-02.

**No reply →** post the pre-written follow-up (§3). **It must not re-open the send decision** — five slips came from exactly that, and three additions are explicitly banned.
**Non-actionable reply →** record it, name which of the three actionable forms it lacks, mark **answered but not actionable**, **send no clarifying question**.
**Actionable reply →** §4's per-thread checklist. ⚠ An option set is **`src/` work with a quality gate**, not a flag.

**P8 alongside:** 8c (close-rule preconditions — **start state, never outcome**) and 8d (re-derive a carried package's *evidence*, not only its conclusion) as CONTRIBUTING rules.

## Days 7–9 (09-10 … 09-12) — P4: sarf · 26 h · + P9 · 2 h · + P10 · 5 h

Branch `planning/sprint39-day7-sarf`.

**⚠ Execute the branch chosen on Day 0.** `SARF_CALLSITE_PLAN.md` §8 states the options; §2 is why: the four sites are **0.5 %** of wall-clock, `gradient.py:453` is **dead code**, and **70.9 %** sits in `compute_constraint_jacobian` — a path Sprint 38 Day 7 already changed.

**The atomic unit:** narrowing of live enumeration sites must land **with** the Jacobian-side column selection. A partial landing is an **inconsistent MCP** — gradient and Jacobian indexed over different column sets — not partial progress.

**Corpus-safety sites that must be provably unperturbed:** `index_mapping.py:634` (assigns `col_id`s — renumbers every column in every model), `constraint_jacobian.py:80`, and the two live complementarity sites.

**⚠ The Day-7 trap, not to be rediscovered:** the first narrowing attempt traded 436 M differentiations for 436 M dict lookups and still did not terminate.

**Mid-track REPLAN:** if a candidate still exceeds **300 s**, **stop and re-attribute rather than iterating.**

**Day 9 also:** P9 records the Epic-5 design in the handoff (2 h — prep delivered it); P10 lands Task 7's **P2 property as a gate** (5 h), which gives every subsequent guard a fail-before.

## Days 10–11 (09-13, 09-14) — Checkpoint 2 · P7 · 13 h · + P5 · 7 h

Branch `planning/sprint39-day10-presolve`.

**⚠ Checkpoint 2 runs FIRST, before P7 changes the recording path.** Running it after would diff against a changed path.

`PRESOLVE_RECORD_REMEDY.md`: **A and B together at `run_full_test.py:936`** — the Day-10 note's `~954` is one of three writes in that branch and the wrong place to gate. **A is a prerequisite for B's durability**; B alone gets overwritten by the next re-solve.

**The remedy invents no category** — weapons' **cold** emit solves (MS-1 @ **1700.397** vs NLP 1735.5696, a 2.03 % divergence), so the correct record is its own cold result and the existing `else` branch already restores it.

**Report the fall with the pre-written wording** (§5, close rule C2). Three figures move: **Match 96→95 · presolve 31→30 · all-219 99→98**. Solve stays 111 and `path_solve_terminated` stays 0.

**Day 11 also starts P5**: guards for the four `NEEDS A GUARD` sites in `POSITIONAL_DOMAIN_SURVEY.md` §2.

## Day 12 (2026-09-15) — P5 finish · 6 h · + P10 · 5 h

Branch `planning/sprint39-day12-audit`.

Tests pinning the nine `ALREADY GUARDED` and seven `NEEDS A TEST` sites. **Do not re-guard the guarded ones** — three independent remedies already exist (consume-once slot claiming, `seen_sym` duplicate bail-out, parser alias substitution).

**⚠ The four `NEEDS A GUARD` sites are candidates, not confirmed defects** — trace each before implementing.

**P10:** work the six P2-flagged models (`dinam`, `egypt`, `gussrisk`, `nonsharp`, `shale`, `turkpow`). ⚠ Two are licence-gated, so their fix is verifiable by property and golden but **not by a solve**.

## Day 13 (2026-09-16) — retest and close · 10 h

Branch `planning/sprint39-day13-close`.

Full retest; determinism **×3** `PYTHONHASHSEED`, byte-identical over the full golden scope; `make check-goldens` **unqualified**.

**Write, in this order:** `SPRINT_LOG.md`, `SPRINT_RETROSPECTIVE.md`, the `SUMMARY.md` row, and **`SPRINT_40_CARRYFORWARDS.md`**.

**⚠ The carryforwards file is a convention, not a prompt item** — S33→S38 unbroken. The next sprint's prep looks for it **by name**. Write it regardless.

**Check every close rule against its precondition** (`PLAN.md` §5) and state each verdict — including any rule that is **VOID**, which is not the same as unmet.

**⚠ Derive every closing figure.** A count of findings is a figure too.
