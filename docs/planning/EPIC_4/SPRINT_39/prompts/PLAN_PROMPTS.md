# Sprint 39 — Per-Day Execution Prompts

**Written by** Prep Task 12 · **2026-09-02** · companion to `../PLAN.md`

**Every day:** branch `planning/sprint39-dayN-<slug>` from `main` → work → **quality gate if any `*.py` changed** (`make typecheck && make format && make lint && make test`) → commit → push → PR → wait for review → reply to each comment on its own thread. **Docs/DB/golden-only PRs skip the gate.**

⚠ **The gate condition is `*.py` ANYWHERE, not just `src/` — and it must be re-evaluated on the PR's FINAL file list, not its first commit.** A review round that adds or edits a script (an `artifacts/*.py` validator, a probe) flips a correctly-waived PR into one that owes the gate, and any "docs only" line already written becomes false. This is the aging-out class: **the claim was true when written and false when merged.** It bit PRs #1723 and #1724 — three CHANGELOG/SPRINT_LOG lines asserting *"no `*.py` changed"* while the PR modified `artifacts/validate_plan.py`.

**Two rules, both derived rather than recalled:**

1. **Never write "no `*.py` changed" as a *waiver reason*.** State the waiver over the stable scope — *"`src/` and `tests/` untouched"* — which a review round adding a docs-side script cannot invalidate. If `*.py` did change anywhere, say the gate was **run rather than waived** and cite its actual result.
2. **Re-derive the condition before every push, including review-round pushes:**

```bash
# Re-run before EVERY push on the branch, not just the first.
PY=$(git diff main...HEAD --name-only | grep -c '\.py$') || true
if [ "$PY" -gt 0 ]; then
  echo "$PY .py file(s) changed — QUALITY GATE REQUIRED; and no doc line may say 'no *.py changed'"
  git diff main...HEAD --name-only | grep '\.py$'
  if git diff main...HEAD -- '*.md' | grep -qE 'no .\*\.py. changed|[Dd]ocs.only'; then
    echo "  ^^ a changed doc line still claims docs-only — FIX IT"
  fi
else
  echo "0 .py changed — gate may be waived"
fi
```

*(`grep -c` exits 1 on zero matches, hence the `|| true`; see the `grep` traps below.)*

⚠ **Run it AFTER committing, before pushing.** It reads `main...HEAD`, so uncommitted working-tree fixes are invisible to it — running it mid-edit reports the state you have just fixed and looks like a false positive. *(Observed while writing this block.)* The doc-line grep is deliberately broad and will also match a line that legitimately **quotes** the phrase in a correction note; read the hit before acting on it.

**Every day — two checkpoints, because the PR body does not exist until the PR does.**

*Before pushing:*

```bash
make check-doc-figures
if git log -1 --format=%B | grep -qE "Co-Authored-By|Generated with"; then
  echo "ATTRIBUTION IN COMMIT MESSAGE — amend before pushing"; exit 1
fi
```

*Before creating the PR* — write the body to a file first, so it can be checked before it is sent:

```bash
if grep -qE "Co-Authored-By|Generated with" /tmp/pr-body.md; then
  echo "ATTRIBUTION IN PR BODY — edit before creating"; exit 1
fi
gh pr create --base main --head <branch> --title "<title>" --body-file /tmp/pr-body.md
```

⚠ **Use `if`, not `&&`, and `-E`, not a BRE.** Two separate traps:

- **`grep` exits 1 on no-match** — that is true of `-c` *and* `-q`; `-q` only suppresses output, it does **not** change the exit code. So `grep -qE … && { …; exit 1; }` returns **1 in the good case** and is fatal under `set -e`. Only the `if` form makes no-match non-fatal while still failing on a match. *(An earlier revision of this file claimed "`-q` makes the good case exit 0". That was wrong — measured: `grep -qE` on a clean file exits **1**.)*
- **`\|` is GNU BRE alternation; POSIX BRE reads it as a literal pipe.** Use `-E` with `|`. That is the exact defect that let a Phase-0 gate pass on the bug it existed to catch (PR #1717).

**⚠ Derive every figure at execution time.** Close rule **C5**. `kpi_block.py` carries its commit and warns on a dirty DB; `floor_tracker.py` reads the provenance file — the mechanical DB count yields **65** and looks authoritative.

---

## Day 0 (2026-09-03) — P1: the floor decision · 4 h · + baseline · 2 h

Branch `planning/sprint39-day0-floor`. **This is a decision, and it blocks the sprint's own baseline.**

Read `FLOOR_DECISION_BRIEF.md`. It does **not** decide — it assembles the evidence, refutes the plan's case for 73 (`polygon`, the named in-corpus precedent, is `likely_convex` exactly like twocge and elec), and makes **74** live via a distinction the plan did not anticipate.

**Deliverables:** the decision recorded in `SPRINT_LOG.md`; if 74 or 75, append to `data/floor_provenance.json` **and update `expected_floor` in the same change** (the tracker exits non-zero on divergence) plus the four downstream sites the brief names. Re-derive the baseline at the settled floor.

**⚠ Also decide P4's branch today** (`PLAN.md` §3) — A keep-as-scoped, B re-scope, or C defer. Day 7 opens on **A** by default. — ✅ **DECIDED 2026-09-03: branch B.** The "A by default" above is the *pre-decision* instruction, retained as the executed record; Days 7–9 execute **B**, which does not implement.

**Gate:** `floor_tracker.py` agrees with the recorded decision; `make check-doc-figures` clean.

## Days 1–3 (09-04 … 09-06) — P2: dyncge · 20 h · + P8 8a/8b · 8 h

Branch `planning/sprint39-day1-dyncge` (and `-day2`, `-day3`).

`ISSUE_1714` has the full Phase-0 gate. **Day 1's first job is to confirm the layer by trace, not to implement** — three of four Sprint-38 gates named the wrong layer, and this one is `src/kkt/stationarity.py` ~7107–7131, the #1081 dim-mismatch branch.

**The controls are pre-registered:** `stat_pq` is correct and must stay **byte-identical**; the residual must reach **`CASE_A`**; the leak gate must drift **dyncge alone**.

**⚠ Do not write new emit logic before checking whether it exists for another population** (P8's 8b, and the lesson dyncge itself produced).

**REPLAN exits:** `PLAN.md` §3.

**P8 alongside:** Day 2 lands **8a** (the layer field + the **added-only** assertion — `pulls.listFiles` already returns `status`; the workflow discards it). Day 3 lands **8b** (the Phase-0 template's *nearest existing mechanism* field). **Both need a fail-before test**; 8a's negative control is that a `modified` doc without a Layer line still **passes**.

## Days 4–5 (09-07, 09-08) — P3: lnts · 18 h · + Checkpoint 1 · 2 h

Branch `planning/sprint39-day4-lnts`.

`LNTS_PROBE_DESIGN.md` fixes the confirm/refute criteria **before** the probe runs — honour that ordering. The collision is confirmed at runtime, and **the banked fix surface is refuted**: `fix_rhs = "0"` at `emit_gams.py:3060–61` **never runs**; the real blanket is **`:3121`**. The machinery to fix it exists — `_fx_eq_name()` at `:711`, the `suppressed` set at `:920`.

**⚠ `cesam` must NOT be batched with lnts.** Same MS-4-at-iteration-0 signature, **0 `_fx_` equations** — a shared signature is not a shared mechanism.

**Day 5 ends with Checkpoint 1:**

```bash
.venv/bin/python scripts/gamslib/run_full_test.py \
  --resolve-changed --since-commit 9ab2c0c3 --min-scope <n>
```

**NO-GO on any `backward` or `missing` row.** It never persists the DB. `--min-scope` is asserted on **discovery**, so set `<n>` to the number of changed goldens you expect — a checkpoint that silently selects zero models passes and proves nothing.

## Day 6 (2026-09-09) — P6: the date gate · 6 h · + P8 8c/8d · 4 h

Branch `planning/sprint39-day6-consultation`.

**⏰ This day cannot move.** Re-read `CONSULTATION_FOLLOWUP_PACKAGE.md` §1 first — it is the only section that goes stale, and it was written 2026-09-02.

**No reply →** post the pre-written follow-up (§3). **It must not re-open the send decision** — five slips came from exactly that, and three additions are explicitly banned.
**Non-actionable reply →** record it, name which of the three actionable forms it lacks, mark **answered but not actionable**, **send no clarifying question**.
**Actionable reply →** §4's per-thread checklist. ⚠ An option set is **`src/` work with a quality gate**, not a flag.

**P8 alongside:** 8c (close-rule preconditions — **start state, never outcome**) and 8d (re-derive a carried package's *evidence*, not only its conclusion) as CONTRIBUTING rules.

## Days 7–9 (09-10 … 09-12) — P4: sarf · 11 h · + P5 · 8 h · + P9 · 2 h · + P10 · 5 h

Branch `planning/sprint39-day7-sarf`.

**✅ The branch was chosen on Day 0: B — re-scope. DO NOT IMPLEMENT.** Prep Task 6 measured the four call sites at **0.5 %** of wall-clock, found **`gradient.py:453` is dead code**, and put **70.9 %** in `compute_constraint_jacobian` — a path Sprint 38 Day 7 already changed. PLAN.md §P4 carries the branch table; `SARF_CALLSITE_PLAN.md` §2 carries the measurement.

- **Day 7 (6 h) — diagnose.** Attribute inside `compute_constraint_jacobian` / `_diff_sum` (the 70.9 %). Produce the attribution, not a fix.
- **Day 8 (5 h) — author the Phase-0 gate** for the differentiation path, so whoever implements it has a fail-before. **No `src/` change lands this sprint.**

**⚠ A CAPPED PROFILE'S TOP FRAME IS WHERE THE RUN *IS*, NOT WHERE THE TIME GOES.** Cumulative attribution is valid only if the phase completed — Task 2 capped short and named `enumerate_equation_instances` the hot path; it is **0.04 %**. Let the profile run to completion or say so explicitly.

**Mid-track REPLAN (applies to B as well):** if a candidate still exceeds **300 s**, **stop and re-attribute rather than iterating.** A second timeout is evidence the lever is in `compute_constraint_jacobian`/`_diff_sum` — different work, different estimate.

**⚠ C6 is VOID under this branch.** Translate reports **135 flat**, naming the re-scope. Do not report +1 Translate → 136; the sprint has **no upward KPI mover**, and that is the pre-registered outcome, not an underperformance.

<details><summary><b>Branch A material — NOT this sprint.</b> Retained for a future revival; do not execute.</summary>

**The atomic unit:** narrowing of live enumeration sites must land **with** the Jacobian-side column selection. A partial landing is an **inconsistent MCP** — gradient and Jacobian indexed over different column sets — not partial progress.

**Corpus-safety sites that must be provably unperturbed:** `index_mapping.py:634` (assigns `col_id`s — renumbers every column in every model), `constraint_jacobian.py:80`, and the two live complementarity sites.

**⚠ The Day-7 trap, not to be rediscovered:** the first narrowing attempt traded 436 M differentiations for 436 M dict lookups and still did not terminate.

</details>

**Day 8 also:** P5 begins (5 h). **Day 9:** P5 continues (3 h); P9 records the Epic-5 design in the handoff (2 h — prep delivered it); P10 lands Task 7's **P2 property as a gate** (5 h), which gives every subsequent guard a fail-before.

## Days 10–11 (09-13, 09-14) — Checkpoint 2 · 2 h · P7 · 13 h · + P5 · 5 h

Branch `planning/sprint39-day10-presolve`.

**⚠ Checkpoint 2 runs FIRST, before P7 changes the recording path.** Running it after would diff against a changed path.

```bash
.venv/bin/python scripts/gamslib/run_full_test.py \
  --resolve-changed --since-commit 9ab2c0c3 --min-scope <n>
```

Same rule: **NO-GO on any `backward` or `missing` row**, `--min-scope` asserted on discovery.

`PRESOLVE_RECORD_REMEDY.md`: **A and B together at `run_full_test.py:936`** — the Day-10 note's `~954` is one of three writes in that branch and the wrong place to gate. **A is a prerequisite for B's durability**; B alone gets overwritten by the next re-solve.

**The remedy invents no category** — weapons' **cold** emit solves (MS-1 @ **1700.397** vs NLP 1735.5696, a 2.03 % divergence), so the correct record is its own cold result and the existing `else` branch already restores it.

**Report the fall with the pre-written wording** (§5, close rule C2). Three figures move: **Match 96→95 · presolve 31→30 · all-219 99→98**. Solve stays 111 and `path_solve_terminated` stays 0.

**Day 11 also starts P5**: guards for the four `NEEDS A GUARD` sites in `POSITIONAL_DOMAIN_SURVEY.md` §2.

## Day 12 (2026-09-15) — P5 finish · 3 h · + P10 · 6 h

Branch `planning/sprint39-day12-audit`.

Tests pinning the nine `ALREADY GUARDED` and seven `NEEDS A TEST` sites. **Do not re-guard the guarded ones** — three independent remedies already exist (consume-once slot claiming, `seen_sym` duplicate bail-out, parser alias substitution).

**⚠ The four `NEEDS A GUARD` sites are candidates, not confirmed defects** — trace each before implementing.

**P10:** work the six P2-flagged models (`dinam`, `egypt`, `gussrisk`, `nonsharp`, `shale`, `turkpow`). ⚠ Two are license-gated, so their fix is verifiable by property and golden but **not by a solve**.

## Day 13 (2026-09-16) — retest and close · 6 h · + P10 · 5 h

Branch `planning/sprint39-day13-close`.

Full retest; determinism **×3** `PYTHONHASHSEED`, byte-identical over the full golden scope; `make check-goldens` **unqualified**.

**Write, in this order:** `SPRINT_LOG.md`, `SPRINT_RETROSPECTIVE.md`, the `SUMMARY.md` row, and **`SPRINT_40_CARRYFORWARDS.md`**.

**⚠ The carryforwards file is a convention, not a prompt item** — S33→S38 unbroken. The next sprint's prep looks for it **by name**. Write it regardless.

**Check every close rule against its precondition** (`PLAN.md` §5) and state each verdict — including any rule that is **VOID**, which is not the same as unmet.

**⚠ Derive every closing figure.** A count of findings is a figure too.
