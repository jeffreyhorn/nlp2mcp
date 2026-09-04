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


## Day 0 (2026-09-03) — P1: the floor decision · 4 h · + baseline · 2 h — ✅ COMPLETE

Branch `planning/sprint39-day0-floor`. **This is a decision, and it blocks the sprint's own baseline.**

Read `FLOOR_DECISION_BRIEF.md`. It does **not** decide — it assembles the evidence, refutes the plan's case for 73 (`polygon`, the named in-corpus precedent, is `likely_convex` exactly like twocge and elec), and makes **74** live via a distinction the plan did not anticipate.

**Deliverables:** the decision recorded in `SPRINT_LOG.md`; if 74 or 75, append to `data/floor_provenance.json` **and update `expected_floor` in the same change** (the tracker exits non-zero on divergence) plus the four downstream sites the brief names. Re-derive the baseline at the settled floor.

**⚠ Also decide P4's branch today** (`PLAN.md` §3) — A keep-as-scoped, B re-scope, or C defer. Day 7 opens on **A** by default. — ✅ **DECIDED 2026-09-03: branch B.** The "A by default" above is the *pre-decision* instruction, retained as the executed record; Days 7–8 execute **B**, which does not implement.

**Gate:** `floor_tracker.py` agrees with the recorded decision; `make check-doc-figures` clean.

**Outcome:** floor **73 → 75**; P4 **branch B**; sprint re-budgeted **140 h → 130 h**; **C6 VOID**.

## Day 1 (2026-09-04) — P2: dyncge — confirm the layer · 9 h — ✅ COMPLETE

Branch `planning/sprint39-day1-dyncge`.

`ISSUE_1714` has the full Phase-0 gate. **Day 1's first job is to confirm the layer by trace, not to implement** — three of four Sprint-38 gates named the wrong layer, and this one is `src/kkt/stationarity.py` ~7107–7131, the #1081 dim-mismatch branch.

**The controls are pre-registered:** `stat_pq` is correct and must stay **byte-identical**; the residual must reach **`CASE_A`**; the leak gate must drift **dyncge alone**.

**⚠ Do not write new emit logic before checking whether it exists for another population** (P8's 8b, and the lesson dyncge itself produced).

**REPLAN exits:** `PLAN.md` §3.

**Outcome — the layer is CONFIRMED but REFINED, and Days 2–3 below are written against the refinement.** The named surface *does* execute (91 hits at the branch, 216 at guard construction) but it is the **symptom** site: it decorates offsets that already exist. The suppression that would stop them being born **never fires once**. Birth site is **~6290–6455**. Evidence: `artifacts/trace_dyncge_layer.py`; written up in `ISSUE_1714` §*Day-1 layer confirmation* and `SPRINT_LOG.md`.

## Day 2 (2026-09-05) — P2: dyncge — the new Pattern-C member · 7 h · + P8 8a · 3 h

Branch `planning/sprint39-day2-dyncge`.

**⚠ Read Day 1's outcome first. Do NOT implement at `~7107–7131`** — Day 1 measured that as the symptom site. Suppressing the `ord()` guard there would leave the wrong answer intact, and the emit would still compile and still solve MS-1, which is exactly how this defect stayed silent.

**The target is the recogniser cascade at ~6290–6455.** All four members miss `pf`, for one shared reason: B-1/B-2/B-3 each require a **single-index `Sum`** (`len(index_sets) == 1` at lines **604 / 743 / 949**) and the launch-shape gate requires a `$` condition dyncge lacks. dyncge's operative term is

```gams
eqXp(i)..  Xp(i) =e= alpha(i)*(sum((h,j), pf(h,j)*F(h,j)) - Sp - Td)/pq(i);
```

a **two-index `Sum` binding BOTH of the variable's coordinates, with the equation index `i` free and unrelated to either.** Day 1 established this is a **distinct Pattern-C member**, not a widening of B-3 — B-3's equation index binds *one* coordinate (cesam2 `COLSUM(jj).. sum(ii, TSAM(ii,jj))`); here it binds **neither**. B-3's *dimension* gate already passes (1 < 2); the miss is the `Sum`'s **arity**.

**⚠ First task of the day, before writing the recogniser: `eqSp` (line 420) carries the IDENTICAL `sum((h,j), pf(h,j)*F(h,j))` term.** It is scalar-domain, so it should take a different branch — **verify that by trace, do not assume it.** A recogniser written for `eqXp` will be offered `eqSp` too. `artifacts/trace_dyncge_layer.py` already wraps all four recognisers; extend it rather than writing a second probe.

**⚠ This is shared, high-blast-radius machinery.** A recogniser that matches too broadly is a **corpus-wide leak**, not a dyncge bug. Two models already rely on the neighbouring members (B-1 claims once, B-3 twice, *within dyncge alone*). Add a **positive requirement**, do not relax an existing exclusion — the S37 fawley lesson: a narrowing predicate that over-fires is fixed by adding a requirement, not subtracting one.

**Phase-0 obligation:** `ISSUE_1714`'s gate predates the refinement. Before the `src/` commit, record the **birth-site** fix surface and a fail-before that fails **at the new location** — a gate that still points at ~7107–7131 would pass against a wrong fix.

**P8 alongside (3 h):** land **8a** — the layer field + the **added-only** assertion (`pulls.listFiles` already returns `status`; the workflow discards it). **Needs a fail-before test**; its negative control is that a `modified` doc without a Layer line still **passes**.

## Day 3 (2026-09-06) — P2: dyncge — verify or hand back · 4 h · + P8 8b · 5 h

Branch `planning/sprint39-day3-dyncge`.

**Run the pre-registered controls, in this order — a non-erroring emit is not a pass:**

1. **Residual** reaches **`CASE_A`** (`scripts/diagnostics/kkt_residual.py`).
2. **`stat_pf`** contains `sum(i, … nu_eqXp(i))` and **zero** `nu_eqXp(j±k)` / `nu_eqII(j±k)` refs and **zero** `$(ord(h) = …)` guards.
3. **Negative control:** `stat_pq` **byte-identical** to before.
4. **Leak gate:** `make check-goldens` drifts **dyncge alone**, unqualified.
5. **Determinism:** ≥ 3 `PYTHONHASHSEED` values, byte-identical.
6. **Objective:** cold MCP currently **MS-1 @ 381401.119** vs NLP **539570.5027**. ⚠ **Assert `modelstat` before reading any objective.**

**REPLAN exits — all three are live, none is remote:**

- residual persists as **`CASE_C_OBJDEF`** ⇒ dyncge is a non-convexity case like elec; the honest target becomes a **documented divergence**, not a Match. elec's own verdict moved `CASE_B` → `CASE_C_OBJDEF` as the classifier improved.
- **any drift beyond dyncge** ⇒ hand back to **#1381** as Pattern C Phase B rather than patching here. Day 1 already routed the work there, so this exit is a *scope* signal, not a failure.
- `stat_pq(HMN)`'s residual survives a corrected `stat_pf` ⇒ a **second, independent defect** (`ISSUE_1714` *Open question*). Record it; do not absorb it into this track.

**P8 alongside (5 h):** land **8b** — the Phase-0 template's *nearest existing mechanism* field. **Needs a fail-before test.** ⚠ This sprint is its own best example: Day 1 found the mechanism existed for three neighbouring populations and still did not cover this one, so the field must record **why the nearest mechanism does not apply**, not merely that one was found.

## Day 4 (2026-09-07) — P3: lnts · 10 h

Branch `planning/sprint39-day4-lnts`.

`LNTS_PROBE_DESIGN.md` fixes the confirm/refute criteria **before** the probe runs — honour that ordering. The collision is confirmed at runtime, and **the banked fix surface is refuted**: `fix_rhs = "0"` at `emit_gams.py:3060–61` **never runs**; the real blanket is **`:3121`**. The machinery to fix it exists — `_fx_eq_name()` at `:711`, the `suppressed` set at `:920`.

**⚠ `cesam` must NOT be batched with lnts.** Same MS-4-at-iteration-0 signature, **0 `_fx_` equations** — a shared signature is not a shared mechanism.

## Day 5 (2026-09-08) — P3: lnts finish · 8 h · + Checkpoint 1 · 2 h

Branch `planning/sprint39-day5-lnts`.

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

## Day 7 (2026-09-10) — P4: sarf — diagnose · 6 h

Branch `planning/sprint39-day7-sarf`.

**✅ The branch was chosen on Day 0: B — re-scope. DO NOT IMPLEMENT.** Prep Task 6 measured the four call sites at **0.5 %** of wall-clock, found **`gradient.py:453` is dead code**, and put **70.9 %** in `compute_constraint_jacobian` — a path Sprint 38 Day 7 already changed. PLAN.md §P4 carries the branch table; `SARF_CALLSITE_PLAN.md` §2 carries the measurement.

**Today: attribute inside `compute_constraint_jacobian` / `_diff_sum` (the 70.9 %). Produce the attribution, not a fix.**

**⚠ A CAPPED PROFILE'S TOP FRAME IS WHERE THE RUN *IS*, NOT WHERE THE TIME GOES.** Cumulative attribution is valid only if the phase completed — Task 2 capped short and named `enumerate_equation_instances` the hot path; it is **0.04 %**. Let the profile run to completion or say so explicitly.

**Mid-track REPLAN (applies to B as well):** if a candidate still exceeds **300 s**, **stop and re-attribute rather than iterating.**

**⚠ C6 is VOID under this branch.** Translate reports **135 flat**, naming the re-scope. Do not report +1 Translate → 136; the sprint has **no upward KPI mover**, and that is the pre-registered outcome, not an underperformance.

<details><summary><b>Branch A material — NOT this sprint.</b> Retained for a future revival; do not execute.</summary>

**The atomic unit:** narrowing of live enumeration sites must land **with** the Jacobian-side column selection. A partial landing is an **inconsistent MCP** — gradient and Jacobian indexed over different column sets — not partial progress.

**Corpus-safety sites that must be provably unperturbed:** `index_mapping.py:634` (assigns `col_id`s — renumbers every column in every model), `constraint_jacobian.py:80`, and the two live complementarity sites.

**⚠ The Day-7 trap, not to be rediscovered:** the first narrowing attempt traded 436 M differentiations for 436 M dict lookups and still did not terminate.

</details>

## Day 8 (2026-09-11) — P4: the Phase-0 gate · 5 h · + P5 · 5 h

Branch `planning/sprint39-day8-sarf`.

**P4 (5 h): author the Phase-0 gate** for the differentiation path, so whoever implements it has a fail-before. **No `src/` change lands this sprint.**

**P5 begins (5 h):** guards for the four `NEEDS A GUARD` sites in `POSITIONAL_DOMAIN_SURVEY.md` §2. ⚠ **They are candidates, not confirmed defects** — trace each before implementing.

## Day 9 (2026-09-12) — P9 · 2 h · + P10 · 5 h · + P5 · 3 h

Branch `planning/sprint39-day9-epic5`.

**P9 (2 h):** record the Epic-5 design in the handoff — prep Task 10 delivered it in full, so this is recording, not designing.

**P10 (5 h):** land Task 7's **P2 property as a gate**, which gives every subsequent guard a fail-before.

**P5 (3 h):** continue the `NEEDS A GUARD` work from Day 8.

## Day 10 (2026-09-13) — Checkpoint 2 · 2 h · + P7 · 9 h

Branch `planning/sprint39-day10-presolve`.

**⚠ Checkpoint 2 runs FIRST, before P7 changes the recording path.** Running it after would diff against a changed path.

```bash
.venv/bin/python scripts/gamslib/run_full_test.py \
  --resolve-changed --since-commit 9ab2c0c3 --min-scope <n>
```

Same rule: **NO-GO on any `backward` or `missing` row**, `--min-scope` asserted on discovery.

`PRESOLVE_RECORD_REMEDY.md`: **A and B together at `run_full_test.py:936`** — the Day-10 note's `~954` is one of three writes in that branch and the wrong place to gate. **A is a prerequisite for B's durability**; B alone gets overwritten by the next re-solve.

**The remedy invents no category** — weapons' **cold** emit solves (MS-1 @ **1700.397** vs NLP 1735.5696, a 2.03 % divergence), so the correct record is its own cold result and the existing `else` branch already restores it.

## Day 11 (2026-09-14) — P7 finish · 4 h · + P5 · 5 h

Branch `planning/sprint39-day11-presolve`.

**Report the fall with the pre-written wording** (`PRESOLVE_RECORD_REMEDY.md` §5, close rule C2). Three figures move: **Match 96→95 · presolve 31→30 · all-219 99→98**. Solve stays **111** and `path_solve_terminated` stays **0**.

⚠ **Match falling to 95 is a CORRECTION, not a regression** — it must be reported with its reason **in the same sentence**.

**P5 (5 h):** continue the audit.

## Day 12 (2026-09-15) — P5 finish · 3 h · + P10 · 6 h

Branch `planning/sprint39-day12-audit`.

Tests pinning the nine `ALREADY GUARDED` and seven `NEEDS A TEST` sites. **Do not re-guard the guarded ones** — three independent remedies already exist (consume-once slot claiming, `seen_sym` duplicate bail-out, parser alias substitution).

**P10:** work the six P2-flagged models (`dinam`, `egypt`, `gussrisk`, `nonsharp`, `shale`, `turkpow`). ⚠ Two are license-gated, so their fix is verifiable by property and golden but **not by a solve**.

## Day 13 (2026-09-16) — retest and close · 6 h · + P10 · 5 h

Branch `planning/sprint39-day13-close`.

Full retest; determinism **×3** `PYTHONHASHSEED`, byte-identical over the full golden scope; `make check-goldens` **unqualified**.

**Write, in this order:** `SPRINT_LOG.md`, `SPRINT_RETROSPECTIVE.md`, the `SUMMARY.md` row, and **`SPRINT_40_CARRYFORWARDS.md`**.

**⚠ The carryforwards file is a convention, not a prompt item** — S33→S38 unbroken. The next sprint's prep looks for it **by name**. Write it regardless.

**Check every close rule against its precondition** (`PLAN.md` §5) and state each verdict — including any rule that is **VOID**, which is not the same as unmet.

**⚠ Derive every closing figure.** A count of findings is a figure too.
