# Owner Decision Brief: Floor Provenance, Corpus Entry & Hosted Runners (Sprint 40 Prep Task 6)

**For:** the owner, before Task 7 · **Prepared:** 2026-10-14 · **Measured at:** `028dc665` (`main`)
**Status:** three decisions posed. Each `## Decision` block ends with one dated owner answer. **No `## Decision` block, question or answer, may be edited after Task 7 starts.** A changed decision becomes a new, dated decision in the sprint's own docs.

**Written blind.** This brief cites **no cohort result**: no licensed solve, convexity classification or comparison verdict for any of the 11 MCP-gated or 9 NLP-gated models. Task 7 has not run. What it does use is about the **toolchain and the code**:
- Task 3's synthetic probes and neutrality sample;
- Task 4's CI design;
- Task 5's schema design;
- Task 2's demo-era parse and translate status;
- the scratch-DB positive control in §1, which uses a model's status as a *label*, not a result.

The PREP_PLAN *Verification* script checks the order mechanically: the last commit that changed any part of a `## Decision` block must be a **strict ancestor** of `COHORT_DRY_RUN.md`'s first commit, and every SHA Task 7 measures at must descend from it.

---

## 1. Why the corpus decision cannot wait: the 142 is derived (Unknown 3.3)

**The 142-candidate denominator is not a list; it is a predicate over the DB:** `convexity.status ∈ {verified_convex, likely_convex}`. Every reader, by grep (`grep -rnE "verified_convex|likely_convex|CONVEX_STATUSES" scripts/ src/`):

| reader | role | effect of a new convex status |
|---|---|---|
| `scripts/sprint_audit/kpi_block.py:45,112` (`compute_kpis`) | **every headline KPI's denominator** | +1 candidate |
| `scripts/sprint_audit/check_doc_figures.py:89` (imports `compute_kpis`) | the doc-figure gate's facts | a touched doc line citing 142 is flagged |
| `scripts/gamslib/run_full_test.py:198–215` (`get_candidate_models`) | **which models the pipeline runs** | the model is parsed, translated and solved on the next full run |
| `scripts/gamslib/batch_parse.py:268–289` (`get_candidate_models`) | batch parse | +1 (it also honours `pipeline_status: skipped`) |
| `scripts/sprint_audit/floor_tracker.py:42,91` | the advisory mechanical count only, never the floor | +1 to a figure labelled "NOT the floor" |

**Positive control (scratch copy outside the repo, deleted afterwards).** `torsion`, one of the NLP-gated models, has `convexity.status: error` today. Setting it to `verified_convex` in the copy:

| | committed DB | scratch DB |
|---|---|---|
| `kpi_block.py --db … --json` → `candidates` | **142** | **143** |
| `run_full_test.get_candidate_models` | 142 (torsion absent) | **143 (torsion present)** |
| `batch_parse.get_candidate_models` | 140 | 141 |

**So a licensed convexity write grows the corpus silently, and on the next pipeline run it also grows what gets solved.** Nothing in today's code stops it. `verify_convexity.py --update-catalog` writes only `catalog.json`, and nothing applies verifier output to the live DB. The first writer that does is Task 5's planned `apply_convexity_results.py` (W10), and **that writer is where the hold lives.**

**Proposed hold mechanism, in effect whichever way Decision 2 goes:**
1. **The committed DB never receives a convex status for an un-admitted model.** W10 (Task 5 §6) refuses any model whose status would *enter* `CONVEX_STATUSES` unless its id is passed in `--admit`. The `--admit` list is the mechanical output of the owner's Decision-2 answer. A refusal exits non-zero and names the model; it never skips silently.
2. **Held models still get evaluated, in a throwaway worktree.** `run_full_test.py` has no `--db` flag and `--model` filters *within* the candidate set, so a held model cannot be run against the committed DB at all. It runs in a throwaway worktree whose own DB copy marks it convex: the Task 3 procedure, retention patch included. Results go into the sprint's docs, and that DB copy is discarded.
3. **Not chosen: a holding status** (e.g. `pending_admission`). It would need a `convexity_result.status` enum change in schema 3.1.0, and every reader above would still have to be audited for it. Refusing at the single writer is narrower.

**Side finding, routed rather than resolved:** `danwolfe` and `decomp` are `pipeline_status: skipped` **and** convex. `kpi_block`'s 142 counts them, but `batch_parse` skips them (140 vs 142), and `PROJECT_PLAN.md` footnote ⁴ describes both as *excluded* at the 147 → 143 step. Whether the historical 142 was meant to include them is not established here. **Routed to Task 12** (a Sprint 40 day item) as a corpus-definition consistency check. It does not affect these decisions.

---

## Decision 1 — Floor provenance: how does a license-unlocked match enter `data/floor_provenance.json`?

### The question

A **license-unlocked match** is a model that matches **only because the licensed edition could finally run it.** Today the 11 MCP-gated models record `path_solve_license`, and an admitted NLP-gated model has never run at all. Does such a match count toward the genuine floor (75 today, `floor_tracker.py`)?

**What the current definition says, read literally.** The floor counts *genuine* matches. *Methodology* matches are excluded: those where the cold emit is byte-identical to pre-fix and the model matches only via the presolve warm start. A license-unlocked **cold** match (`model_optimal` + match, no warm start) is **not** a methodology match, and the baseline of 73 already counts cold matches no fix ever touched. **So the definition as written admits license-unlocked cold matches.** Excluding them requires **amending the definition**, which the Sprint 39 brief §5 also required of its "never genuine" reading.

**Mechanics (`floor_tracker.py`):** `floor = baseline.count + len(entries)`. **Every entry counts +1 whatever its `limb`**: the limb is a label, not a filter. `expected_floor` must change in the same edit, or the tracker exits non-zero. The floor is **in-corpus only** (baseline note), so an NLP-gated model can enter it only if Decision 2 admits it.

### Options

| | A. Count it: new limb | B. Don't count it: separate ledger | C. Don't count it, don't record it |
|---|---|---|---|
| **rule** | each license-unlocked cold match is an `entries` item with `limb: "license-unlocked-cold-match"` | each is recorded in a **new, non-counting** `license_unlocked` list in `floor_provenance.json`; the floor is unchanged | the floor is unchanged; the matches appear only in `SPRINT_LOG.md` |
| **floor at close** | 75 + *k* | 75 (and *k* reported beside it) | 75 |
| **report line** | "floor 75 → 75+*k* (*k* license-unlocked)" | "floor 75 (+*k* license-unlocked, not counted)" | "floor 75" |
| **definition** | unchanged (the literal reading) | **amended**: license-unlocked matches excluded, kept auditable | **amended**; not auditable from data |
| **tooling** | none | `floor_tracker.py` lists the ledger, labelled *not in the floor* (small change + test) | none |

**Applies under every option:**
- **A presolve-only (warm-start) match** of an unlocked model is handled by the **existing** rule. It is methodology, not counted, unless an emit fix changed its cold emit.
- **The fixed-but-never-runnable case.** A model whose cold golden was changed by an emit fix in an earlier sprint but could never run until now:
  - **Recommended sub-rule (fail-before):** credit it as **fix-driven genuine** (the existing `cold-match` / `presolve-match-genuine` limbs) **only if its pre-fix golden, run under the license, does *not* match.** That is the same fail-before evidence any fix needs.
  - **Otherwise** it is license-unlocked like the rest.
  - The sub-rule is written now, so it can't be fitted to the results.

### The case for A

- **It is what the definition says.** The floor exists to separate genuine matches from warm-start *methodology* artifacts. A cold match is the strongest evidence the pipeline has, licensed or not.
- **Leaving it out understates the floor:** a model the emit already handled correctly would be uncounted only because the demo could not show it.
- **No new tooling, no amendment.**

### The case for B (and against A)

- **The floor is reported as a series**, and the Sprint 39 → 40 step would then mix two causes: engineering (fixes) and **measurement capability** (the license). A one-sprint jump of up to +11 would read as emit progress that no emit change produced.
- **That is the distortion the Sprint 23–25 scope footnotes (³, ⁴, ⁶) avoided:** they reported scope changes beside the series instead of re-basing it silently. B is that precedent applied to the floor.
- **Unlike C, B keeps every unlocked match auditable**, per model, in the same file. A later sprint can fold the ledger into the floor with a single explicit edit if the owner chooses.
- **C is B without the audit trail.** It saves only a small tooling change.

### Recommendation

**B, with the fail-before sub-rule.** This is the brief's recommendation, not a decision.

### Exact edits

- **If A:**
  - Append to `data/floor_provenance.json` → `entries`, per matched model: `{"model_id": "<id>", "limb": "license-unlocked-cold-match", "since_sprint": 40, "evidence": "first licensed run at <sha>: model_optimal + match (cold); emit unchanged since <golden sha>; was path_solve_license", "pr": "<n>"}`.
  - Raise `expected_floor` by the same *k* **in the same change**.
  - Add one `_README` line naming the limb.
  - Re-baseline `SUMMARY.md` and `PROJECT_PLAN.md` (the S39 brief §5's four-site table), then run `make check-doc-figures`.
- **If B:**
  - Add a top-level `"license_unlocked": []` list to `data/floor_provenance.json` with the same entry schema, **never** read by `compute_floor`.
  - Add a `_README` paragraph amending the definition.
  - `floor_tracker.py`: print the ledger as `+ <id> [license-unlocked] … NOT in the floor`, include it in `--json` as `license_unlocked_NOT_in_floor`, and add a test that a ledger entry leaves `floor` and `expected_floor` unchanged.
  - `expected_floor` stays **75** unless a fix-driven entry is earned under the sub-rule.
- **If C:** add a `_README` paragraph amending the definition, and a `SPRINT_LOG.md` entry per unlocked match. No code change.

**Owner answer (2026-10-14):** **B — separate ledger.** License-unlocked matches are recorded in a new, non-counting `license_unlocked` list in `data/floor_provenance.json`, and the floor stays at 75 (+*k* reported beside it). The definition is amended accordingly. The fail-before sub-rule applies: a model whose emit was fixed in an earlier sprint is credited as fix-driven genuine only if its pre-fix golden, run under the license, does not match.

## Decision 2 — Corpus entry: may NLP-gated models enter the 142-candidate corpus?

### The question

Nine NLP-gated models are in scope by type: `airsp`, `airsp2`, `emfl`, `indus89`, `jbearing`, `minsurf`, `msm`, `phosdis`, `torsion`. `andean` is a MIP and is **excluded, never relaxed**. The demo refused their reference NLP solve, so their convexity was never classified. Admitting any of them moves every headline denominator off 142 (to at most 151). **What is the admission rule?**

**What is already known, and is not a cohort result** (Task 2, demo-era, no GAMS solve involved):
- 6 of the 9 parse;
- **4** reach a translated MCP (`airsp2`, `jbearing`, `minsurf`, `torsion`);
- 2 time out at 600 s (`airsp`, `msm`);
- 3 fail to parse (`emfl`, `indus89`, `phosdis`).

So whatever the rule, **at most 4 can reach Solve without P3 grammar or translate work.** An admitted model that cannot translate lowers Translate, Solve and Match *rates* on the new denominator.

### Options

| | A. Admit by rule | B. Admit case by case | C. Hold at 142 for Epic 4 |
|---|---|---|---|
| **rule** | a model is admitted **if and only if** the licensed `verify_convexity.py` classifies it `verified_convex` / `likely_convex`, the predicate every current candidate already meets | the owner reviews each classified model at a mid-sprint checkpoint | none admitted in Sprint 40; the set is evaluated and recorded as **Epic 5 scope** |
| **written blind?** | **yes**: the rule is fixed now, and the admitted set follows mechanically | **no**: each decision is taken *after* that model's result exists, the pattern this brief exists to avoid | yes |
| **denominators** | 142 (continuity) **and** 142 + *k* (expanded), both reported | same, *k* chosen | 142 only; the set's results reported separately |
| **hold (§1)** | W10 `--admit` = the rule's output | `--admit` = the owner's per-model list | W10 run with **no** `--admit`; all nine evaluated in a throwaway worktree only |
| **risk** | admits models that do not translate (rates fall on the new denominator); disclosed, not hidden | fitted to results | the corpus understates what the toolchain can now reach until Epic 5 |

### Reporting both denominators in one sentence (A or B)

The template, on the Sprint 23–25 footnote precedent:

> *Match **M**/142 (**x %**) on the continuity corpus; **M′**/**142+k** (**y %**) on the expanded corpus, which admits **k** NLP-gated models by the Sprint 40 rule (footnote ⁹). Neither figure counts an admission as a recovery.*

**One rule for every headline KPI** (Parse, Translate, Solve, Match): the continuity figure leads, the expanded figure follows in the same sentence, and a footnote names the admitted models and the rule.

### The case for A

- **It is the only admission rule that can be written blind.**
- It is the **same predicate the existing 142 already satisfies**, so it adds no new bar, only the ability to measure.
- The continuity figure is kept beside the new one, so no series is broken.

### The case for C (and against A)

- **Epic 4 is a fixed-scope epic in its last sprints.** A denominator change in Sprint 40 makes Sprints 41–43's targets ("≥ 64 % of pipeline scope") ambiguous unless every one of them is restated.
- Five of the nine cannot translate today, so on the expanded corpus the rates fall for reasons that are P3 grammar work, not emit quality.
- **C gives up nothing in evidence:** the nine are still evaluated and reported, just outside the headline.

### Recommendation

**A, reported with both denominators.** It is the blind rule, and the continuity figure keeps the Epic 4 series intact. **B is not recommended**: it is a decision taken after the result. **C is the conservative alternative** if the owner prefers not to restate the remaining Epic 4 targets.

### Exact edits

- **If A or B:**
  - **New `data/corpus_admissions.json`:** one entry per admitted model (`model_id`, `admitted_sprint: 40`, `rule` (`"verifier-convex"` for A, or the owner's note for B), `classification`, `license_edition`, `evidence`, `pr`).
  - **W10 runs with `--admit $(ids from that file)`.**
  - **`kpi_block.py` gains `--corpus continuity|current`** (default `current`). `continuity` drops ids listed in `corpus_admissions.json`, so **both denominators derive mechanically, and neither is a hand count.** Add a test that `continuity` on today's DB equals today's `current` (142).
  - **`check_doc_figures.py` gains a `candidates_continuity` fact** beside `candidates`.
  - **A `PROJECT_PLAN.md` Rolling-KPIs footnote ⁹** for the S40 column, plus the S41–S43 target lines restated as "≥ x % (continuity) / ≥ y % (expanded)".
- **If C:**
  - No admission edit; W10 runs with **no** `--admit`.
  - The nine's results go to `COHORT_DRY_RUN.md` / the P3 doc and to an **Epic 5 scope note** in `PROJECT_PLAN.md`.
  - The Rolling-KPIs **S40 "Valid Corpus Defined" cell** records "held at 142 (owner, <answer date>)".

**Owner answer (2026-10-14):** **A — admit by rule.** An in-scope NLP-gated model enters the corpus if and only if the licensed `verify_convexity.py` classifies it `verified_convex` / `likely_convex`. Every headline KPI is reported with both denominators (142 continuity and 142 + *k* expanded) in one sentence, with a Rolling-KPIs footnote. `andean` stays excluded as MIP.

## Decision 3 — CI license use: hosted runners, and the `gams-licensed` environment

### The question

May the license be used in CI, and if so how? This decision is posed **complete**. Task 3's binding evidence and Task 4's checklist are both prerequisites of this task, and both are carried below.

**Task 3 evidence (`LICENSE_PROBE.md` §6):**
- The effective license is an **evaluation** license that expires **2027-09-21**.
- Its run-time header carries **node, memory and core-count fields**, so it is **node-locked in shape**.
- Its terms for other machines are **not determinable from the file**.

**Task 4 evidence (`CI_LICENSE_DESIGN.md`):**
- **Branch policy:** a `main`-only environment **refuses** other branches on `push`, `pull_request` and `workflow_dispatch`, verified empirically.
- **GAMS documentation:** a **local** license embeds a permanent node ID, and *"dynamic environments like Docker containers or virtual machines are unsuitable for local licenses"*. A **network** license fits hosted CI.
- **Runner restriction:** a self-hosted runner **cannot** be restricted to one workflow on a personal-account repo.
- **Recommendation:** the licensed tier is **local-only** for Sprint 40.

**Task 4's owner checklist (§7), carried verbatim:**

1. **License terms (GAMS):** is this evaluation license **local** or **network**? If local, may its access code be activated per job on GitHub-hosted ephemeral runners, and does each activation consume anything? If not, can GAMS provide a **network** license (or a CI-usable one) for `licensed-solve.yml`?
2. **Runner model:** accept **local-only** licensed runs for Sprint 40 (recommended), or move the repository to an organization to enable a self-hosted runner group restricted to `licensed-solve.yml@refs/heads/main` (pinned to the ref, not just the path; §5).
3. **Environment (only if a CI-usable license arrives):** create `gams-licensed` with a **`main`-only** deployment-branch policy; decide whether it **requires reviewers**.
4. **Secret placement:** store the access code as `GAMS_ACCESS_CODE` **in the environment only** — never as a repository secret, and never the license file.
5. **Machine-wide license on this machine (no file copying):** activate from the access code into the machine-wide data directory: `sudo "/Library/Frameworks/GAMS.framework/Versions/54/Resources/gamsgetkey" <access-code> -o "/Library/Application Support/GAMS/gamslice.txt"` (create the directory first). GAMS searches it **second**, after the user-level directory and before the system directory, so a different user or `HOME` no longer falls back silently to the demo. It also lives **outside** the GAMS install, so an upgrade or reinstall cannot overwrite it, removing the caution in Task 3's §5. Confirm afterwards with a `sudo -u <other user>` run of an over-ceiling probe classified `licensed`. ⚠ Same open question as item 1: whether a second activation on this machine counts against the license.
6. **PyPI publishing (pre-existing, not GAMS):** put the publish job behind a **protected environment in every variant** — tokens as environment secrets, or a trusted publisher configured **with that environment** (trusted publishing without it still accepts a branch copy of the workflow). Then enforce authorization **outside the workflow**, because a tag supplies its own YAML: either **(A)** publish from `main` only (environment `main`-only, no `release` trigger), or **(B)** keep tag-triggered publishing with **required environment reviewers plus a tag ruleset** limiting `v*` tags to maintainers. An in-job ancestry check is additional validation only, never a substitute for (A) or (B). In either case, split build (secretless) from publish (environment + `id-token: write`, runs no repository code). Today one job holds `id-token: write` while it runs the tagged code's tests, and both a dispatch on any branch and a release from an off-`main` tag run unreviewed code with the tokens (§1).
7. **Delete the throwaway repository:** `gh auth refresh -h github.com -s delete_repo && gh repo delete jeffreyhorn/nlp2mcp-envpolicy-probe-20261013 --yes` (it is archived and holds no secret or environment).

*Items 5–7 are owner actions that stand under every option below. Items 1–4 are what this decision settles.*

### Options

| | A. Local-only for Sprint 40 | B. Hosted CI, gated on GAMS | C. Organization + self-hosted runner |
|---|---|---|---|
| **what runs licensed** | the owner's machine only (throwaway worktree + retention patch), every row stamped `license_edition` (Task 5) | `licensed-solve.yml` on GitHub-hosted runners, **once GAMS confirms** a CI-usable (network) license | `licensed-solve.yml` on a dedicated self-hosted runner in an org runner group pinned to `licensed-solve.yml@refs/heads/main` |
| **`gams-licensed` environment** | **not created** in Sprint 40 | created: `main`-only, secret `GAMS_ACCESS_CODE`, reviewers per the sub-answer | created as in B |
| **post-merge large-model coverage** | none in CI; local runs per batch | automatic on every push to `main` | automatic, as B |
| **blocks Sprint 40?** | no | P1's CI half waits on GAMS, and REPLANs to A if they decline | repository transfer and runner setup, outside the sprint's scope |
| **PR workflows** | demo-only, plus Task 4 §6's change (classify the edition; skip over-ceiling models with a notice) | same | same |

**Sub-question if B or C:** should `gams-licensed` **require reviewers**? With reviewers, each run waits for a maintainer, which is safer against a compromised `main` but slows nightly runs. Without them, `main`-only is the whole control.

### Recommendation

**A for Sprint 40, and send the GAMS question (checklist item 1) now**, so B is ready to adopt in a later sprint if GAMS offers a network license. C is not recommended: it changes repository ownership to work around a licensing question GAMS can answer.

### Exact edits

- **If A:**
  - No workflow file and no environment.
  - `PROJECT_PLAN.md` Sprint 40 P1 "Owner prerequisites" and the CI bullets: record **"CI half: local-only for Sprint 40 (owner, <answer date>)"**.
  - P1 still lands Task 4 §6's PR-side change.
  - The GAMS question goes out as checklist item 1.
- **If B:**
  - Create the environment: `gh api -X PUT repos/jeffreyhorn/nlp2mcp/environments/gams-licensed` with a `main`-only deployment-branch policy (custom policy, branch `main`). Add reviewers if the sub-answer says so.
  - Add the secret with `gh secret set GAMS_ACCESS_CODE --env gams-licensed`.
  - Add `.github/workflows/licensed-solve.yml` from `CI_LICENSE_DESIGN.md` §3, landed **only after** GAMS confirms the license type.
- **If C:** transfer the repository to an organization, create a runner group whose *selected workflows* is pinned to `<org>/nlp2mcp/.github/workflows/licensed-solve.yml@refs/heads/main`, then do as B.

**Owner answer (2026-10-14):** **B — hosted CI, gated on GAMS.** Create `gams-licensed` (`main`-only deployment-branch policy, **no required reviewers**, secret `GAMS_ACCESS_CODE` in the environment only) and land `licensed-solve.yml` **once GAMS confirms** a CI-usable (network) license. If GAMS declines, this REPLANs to A (local-only). Until GAMS answers, licensed runs are local.

---

## 2. Consequences for Sprint 40's reported figures, by answer

| figure | depends on | how it is reported |
|---|---|---|
| Solve, Match (142 continuity) | the MCP-gated cohort (in-corpus) | every cohort move reported as **license-unlocked, not recovered** (`PROJECT_PLAN.md` P2) |
| Solve, Match (expanded) | Decision 2 | only under A/B; same sentence as the continuity figure |
| genuine floor | Decision 1 (and Decision 2 for NLP-gated models) | A: the floor moves; B: 75 plus a ledger count; C: 75 |
| CI coverage of large models | Decision 3 | A: none in CI; B/C: post-merge |

## 3. What this brief does not do

It cites no cohort result, runs no licensed solve of any gated model, and edits no data file. The positive control used a scratch copy outside the repository, and `git status -- data/` is clean.
