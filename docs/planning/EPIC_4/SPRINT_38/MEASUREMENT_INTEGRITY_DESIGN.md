# Sprint 38 Prep Task 3 — Measurement-Integrity Design (P6)

**Date:** 2026-08-17 · **Branch:** `planning/sprint38-task3` · **Measured at:** `1a252648` · **Scope:** design + live fail-before reproduction. No `src/`, DB, golden or `scripts/` change.

**Verdict: 🔶 DESIGN COMPLETE, WITH TWO ASSUMPTIONS REFUTED.** All four sub-deliverables are specified. Two of the four unknowns did **not** hold as written, and both make P6 *smaller and sharper* than planned:

1. **`leak-check` already fails correctly.** The banked premise — that a `NO-OP` is "mistakable for a pass" — is **wrong**: `make leak-check MODEL=sarf` exits **2**. The real defect is the *diagnostic*, which asserts a byte-identity that was never measured.
2. **The floor provenance file cannot reproduce 76 — or any figure — from existing artifacts.** Three independent derivations give **65**, **93** and **76**, and the 76 credits three out-of-corpus models while leaving ~62 unattributed. The tracker must be **append-only from a declared baseline**, not reconstructed.

---

## 1. The four sub-deliverables at a glance

| sub | what it closes | status after this task |
|---|---|---|
| **6a** derived-figure helper | banked staleness (S37 ×3) | designed |
| **6b** gate-scope assertions | one **confirmed** silent defect + one **misdiagnosis** | designed, scope halved |
| **6c** floor provenance | the floor is unauditable | designed as **append-only**; baseline is an owner decision |
| **6d** re-anchor | a 4-sprint-stale anchor | `8cffec29` chosen, **conditional on 6b** |

---

## 2. 6a — the derived-figure helper

**Problem.** Sprint 37 quoted figures into documents that went stale within 24 hours — the Day-8 prompt sweep was re-staled by Day 9's own re-baseline, and the refuted "+2 or 0" reached the close doc. Task 2 then found two more banked figures that no longer hold.

**Design.** A `scripts/sprint_audit/kpi_block.py` entry point:

```
usage: kpi_block.py [--json] [--at-sha <commit>]
```

- **Human form** (default) — a paste-ready block:
  ```
  Solve 108 · Match 94 (65 cold + 29 presolve) · Translate 135 · mi 7 · pse 6 · all-219 97
  measured at 1a252648
  ```
- **Machine form** (`--json`) — `{"solve":108,"match":94,"cold":65,"presolve":29,...,"sha":"1a252648"}` for templates and CI.
- **`--at-sha <commit>` selects *which commit to measure*** — it reads the DB at that revision (`git show <commit>:data/gamslib/gamslib_status.json`) instead of the working tree. Default is `HEAD`. Useful for regenerating a historical figure *with its correct provenance* rather than re-quoting one.
- **The measured-at SHA is ALWAYS in the output, in both forms. There is no flag that selects, suppresses or overrides it** — it is derived from whatever revision was actually read. A figure without provenance is exactly what this helper exists to prevent, so no mode can produce one.

**Note on the flag name:** an earlier draft called this `--sha`, which was ambiguous between "print the sha" and "select a commit". The rename resolves that: `--at-sha` *only* selects, and printing is unconditional.

**Derivation contract (fixed here so it cannot drift):** corpus = `convexity.status ∈ {likely_convex, verified_convex}`; keys = **`model_id`** (never `model_name`, which holds the description); fields = `mcp_solve.outcome_category` + `solution_comparison.comparison_status`; Translate = `nlp2mcp_translate.status == 'success'`. These are the exact keys whose misuse produced the S37 Day-0 "Solve 0 / Match 0" error.

**The genuine floor is deliberately NOT emitted by this helper** — see §4. Emitting it would imply it is derivable, which is the error the helper exists to prevent.

**Rule for documents:** a figure may be quoted only with the commit it was measured at. Prompts should call the helper rather than embed numbers.

## 3. 6b — gate-scope assertions

### 3.1 `--resolve-changed` — ❌ silent defect CONFIRMED

**Reproduced live** at `1a252648`. `_changed_golden_model_ids()` runs `git diff --name-only <since>..HEAD -- data/gamslib/mcp/`, so it sees **committed** history only:

```
# with data/gamslib/mcp/chenery_mcp.gms modified in the working tree:
_changed_golden_model_ids('8cffec29') -> []      # chenery INVISIBLE
_changed_golden_model_ids('1a252648') -> []      # empty selection, dirty tree
```

An uncommitted golden edit is invisible, and an empty selection currently produces a **GO** verdict. This is the mechanism behind the Sprint-37 false GO.

**Assertion:**

| condition | verdict | exit |
|---|---|---|
| selection non-empty, all buckets held | `GO` | 0 |
| selection **empty** AND `git status --porcelain data/gamslib/mcp/` **clean** | `GO (VACUOUS — no goldens changed since <sha>)` | 0 |
| selection **empty** AND working tree has modified/untracked goldens | **`NO-GO: <n> golden(s) modified in the working tree are invisible to --resolve-changed (it selects by git diff). Commit them, then re-run.`** | **2** |

The third row is the defect. The second row must stay a pass — see §5.

### 3.2 `leak-check` NO-OP — ⚠ the assumption was WRONG

The banked premise was that a golden-less model yields a `NO-OP` "mistakable for a pass". **It is not.** Measured live:

```
$ make leak-check MODEL=sarf
Golden staleness: checked 163 in-scope golden(s) (7 allowlisted, 3 workers).
  NO-OP: expected drift on sarf but the emit was byte-identical — the fix did not change the emit.
make: *** [leak-check] Error 1
>>> EXIT CODE: 2
```

`missing = expected - drifted_models`, and a model with no golden can never enter `drifted_models`, so it lands in `missing` and drives `ok = False`. **The exit code is already correct.**

**The real defect is the diagnostic.** For sarf there is no `sarf_mcp.gms` at all, so *nothing was compared* — yet the message asserts "the emit was byte-identical" and diagnoses "the fix did not change the emit". Both claims are about a comparison that never happened. A maintainer would go looking for why their fix was inert; the actual answer is "this model has no golden."

This is the sprint's recurring shape once more: **a message asserting a property that was never measured.**

**Assertion:** split `missing` by whether a golden exists.

| case | verdict | exit |
|---|---|---|
| golden exists, did not drift | `NO-OP: expected drift on <m> but the emit was byte-identical — the fix did not change the emit.` (unchanged) | 2 |
| **no golden exists** | **`UNVERIFIABLE: <m> has no committed golden (data/gamslib/mcp/<m>_mcp.gms) — nothing was compared. This is not a leak result. If <m> is expected to produce a golden, create it; otherwise use --expect-new <m>.`** | 2 |

**Scope note:** 6b is roughly **half the work planned**, because one of its two targets already behaves correctly. The saving should be recorded, not silently absorbed.

## 4. 6c — the floor provenance file

### 4.1 The floor is not derivable — three derivations, three answers

| method | result | why it fails |
|---|---|---|
| mechanical `Match − (presolve ∧ match)` | **65** | drops the "a fix changed the cold emit" limb entirely |
| golden-changed-ever (git log per golden) | **93** | 28 of 29 presolve goldens have >1 commit; regeneration happens for many reasons unrelated to a correctness fix |
| the documented provenance chain | **76** | credits **3 out-of-corpus** models (`ps2_f_s`, `ps2_s`, `ps3_s_gic`, all `non_convex`); only **14 of 76** attributable by name; ~62 sit in an unnamed "S28 genuine 68" block with no per-model record |

The middle row is this task's new evidence, and it is decisive: **"did the golden change?" is mechanical, but "did a *real fix* change it *for this model's correctness*?" is a judgement**, and no repo artifact records that judgement.

### 4.2 Consequence — the tracker must be append-only

A tracker that *reconstructs* the floor is impossible. A tracker that *accumulates* it is straightforward:

```yaml
# data/floor_provenance.yaml
baseline:
  count: <DECLARED>          # an owner decision — see 4.3
  as_of: <sprint>
  note: "Opaque block; per-model records were never kept. Not reconstructible."
entries:
  - model_id: markov
    limb: cold-match
    since_sprint: 37
    evidence: "P1 σ=sp discriminator; presolve→cold with match retained"
    pr: 1665
  - model_id: sample
    limb: cold-match
    since_sprint: 33
    evidence: "P6 pruned-var .l-init fix; path_syntax_error→model_optimal+match"
```

**`floor = baseline.count + len(entries)`.** Every future movement adds an entry with its evidence; the opaque baseline is never re-litigated. Within two or three sprints most *movement* is auditable even though the base is not.

**Fail-loud rule:** the tracker asserts its total against a `expected_floor` value committed alongside it, and **exits non-zero on divergence** rather than reporting its own number. It never emits a floor derived from the DB — that path yields 65 and would look authoritative.

### 4.3 The baseline is an owner decision, not a measurement

Task 2 established the floor's provenance credits three out-of-corpus models. This task confirms it cannot be reconstructed either way. So the baseline must be **declared**:

| option | baseline | implication |
|---|---|---|
| **(a) in-corpus only** | **73** | the floor has been overstated by 3 since Sprint 31; every S31–S37 report is off by 3 |
| **(b) keep the historical figure** | **76** | the floor's scope differs from Solve/Match's, and that must be written into `reference_match_kpi_corpus_scope` |

**This task does not choose.** Both are defensible; the choice changes six sprints of reported history and is the owner's. **Recommendation: (a)**, because the floor is reported in the same breath as Solve and Match, which are strictly in-corpus, and a metric whose corpus differs silently from its neighbours is the more dangerous of the two states. But (b) with an explicit written scope is also coherent, and cheaper.

**Whichever is chosen, it must be recorded in the file's `baseline.note` with the reasoning** — that record is the artifact that stops this recurring.

## 5. 6d — the re-anchor

**Selections measured at `1a252648`:**

| anchor | | selects |
|---|---|---|
| `78ceaead` | S34 close — **current**, 4 sprints old | **19** models |
| `935d94b7` | S36 close | 2 (fawley, markov) |
| **`8cffec29`** | **S37 close — the candidate** | **0** |
| `1a252648` | HEAD | 0 |

**DB-modifying commits:** `78ceaead..HEAD` = 3 · `8cffec29..HEAD` = 0.

**Decision: re-anchor to `8cffec29`** — the DB changed in Sprint 37, so drift *since then* is what Sprint 38 must watch, and the 19-model selection at the stale anchor re-solves four sprints of settled history on every checkpoint.

**But the candidate selects zero, and that is exactly the hazard 6b addresses.** Re-anchoring today makes the checkpoint **vacuous at sprint start** — it would report GO while checking nothing. That is *semantically correct* (nothing has drifted yet) and *operationally dangerous* under the current code, which cannot distinguish "nothing changed" from "I looked in the wrong place".

**⇒ 6d is CONDITIONAL on 6b landing first.** Re-anchoring without the empty-selection assertion trades a slow checkpoint for a silent one. Sequence: **6b, then 6d, in that order, in the same sprint.**

**Cost of re-anchoring:** the S34–S37 drift (19 models) stops being re-verified on every run. That drift is already settled — those buckets were confirmed at each sprint's close — so the cost is re-verification of history, not loss of signal.

## 6. 6.4 — false-positive modes (why a guard gets disabled)

An over-firing assertion gets bypassed by habit, restoring the original defect with extra ceremony. Enumerated:

| # | legitimate state | naive assertion would | design response |
|---|---|---|---|
| 1 | **Empty selection at sprint start** — no goldens changed since the anchor. This is the *normal* state after re-anchoring (§5). | fail every run until the first golden lands | `GO (VACUOUS)` at exit 0, distinguished by a **clean working tree** |
| 2 | **A golden-less model named in `--expect-drift`** — sarf before its re-arch lands | hard-fail, tempting `--allow-*` bypass | distinct `UNVERIFIABLE` verdict + a `--expect-new <m>` flag for the create-a-golden case |
| 3 | **Docs-only PR touching no goldens** | fail the required check on every docs PR | scope assertions apply only when `--expect-drift`/`--since-commit` is given |
| 4 | **A deliberately narrowed sweep** (`--models`) during local iteration | block local work | already handled — `subset_scope` downgrades the claim to `PARTIAL` rather than failing |

**Escape-hatch policy.** Any bypass (`--allow-unverified`, `--expect-new`) must **print the caveat into the verdict line**, exactly as `subset_scope` already does — the existing `LEAK GATE PASS (PARTIAL — NOT a full-corpus leak claim)` is the model. A bypass that leaves no trace in the pasted evidence is how a gate quietly stops being one.

**Detecting over-use:** the `skip-phase0` label precedent applies — bypasses are visible in CI logs and can be counted per sprint. If a bypass appears in more than a couple of PRs, the assertion is miscalibrated and should be re-tuned rather than tolerated.

## 7. Implementation order for the sprint

1. **6b** — the two assertions (smaller than planned; `leak-check` needs only the message split)
2. **6d** — re-anchor, *after* 6b, so the vacuous-selection case is guarded
3. **6c** — provenance file, *after* the owner declares the baseline (§4.3)
4. **6a** — the helper; independent, can land any time

## 8. Reproduction

```bash
# 6b(i) — uncommitted golden invisible to --resolve-changed
printf '\n* probe\n' >> data/gamslib/mcp/chenery_mcp.gms
.venv/bin/python -c "import sys; sys.path.insert(0,'scripts/gamslib'); \
  from run_full_test import _changed_golden_model_ids; print(_changed_golden_model_ids('8cffec29'))"
git checkout -- data/gamslib/mcp/chenery_mcp.gms      # -> [] : chenery invisible

# 6b(ii) — leak-check on a golden-less model (SLOW: sweeps all 163)
make leak-check MODEL=sarf; echo "exit=$?"            # -> NO-OP message, exit 2

# 6c — the three derivations
#   mechanical -> 65 ; golden-changed-ever -> 93 ; documented chain -> 76

# 6d — anchor selections
.venv/bin/python -c "import sys; sys.path.insert(0,'scripts/gamslib'); \
  from run_full_test import _changed_golden_model_ids; \
  print({a: len(_changed_golden_model_ids(a)) for a in ['78ceaead','935d94b7','8cffec29']})"
```

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 3. All four sub-deliverables designed; **6.1 partially refuted** (leak-check already fails correctly), **6.2 refuted** (the floor is not reconstructible), **6.3 verified conditional on 6b**, **6.4 verified**. One decision is escalated to the owner: the floor baseline, 73 or 76.
**Last Updated:** 2026-08-17 · **Owner:** Sprint 38 execution team
