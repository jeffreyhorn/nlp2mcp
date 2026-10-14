# Sprint 40 License Probe (Prep Task 3)

**Measured at:** `35b296b3` (`main`) · **Date:** 2026-10-13 · **Toolchain:** GAMS 54.2.1

**License hygiene:** this document records the **edition only** (`licensed` / `demo`) and non-identifying GAMS markers. No license-file content, `Licensee:` / `USER:` licensee text, license-ID, node or memory field appears here — those were inspected locally and never copied. The demo refusal lines quoted in §2 are GAMS's generic messages.

---

## 1. Which license file does GAMS read? (precedence — Unknown 1.1)

**Executables.** Every pipeline path resolves to **one** binary, `/Library/Frameworks/GAMS.framework/Versions/54/Resources/gams` (54.2.1):

| caller | how it finds `gams` | resolves to |
|---|---|---|
| `verify_convexity.py::verify_model` | bare `gams` on `PATH` | `…/Versions/54/Resources/gams` |
| `test_solve.py::solve_mcp` | prefers `…/Versions/Current/Resources/gams` | `Current → 54` → same binary |
| `kkt_residual.py` | `_GAMS_CANDIDATES` → `…/Versions/Current/…` first | same binary |

GAMS 51 and 53 are also installed (each with its own system-directory license file), but **nothing in the pipeline invokes them**.

**Two license files exist:** the **user-level** `~/Library/Application Support/GAMS/gamslice.txt` (dated 2026-10-12, with a `.~bk` backup beside it — consistent with GAMS Studio's license installer) and the **system-directory** `…/Versions/54/Resources/gamslice.txt` (the 2026-07-13 demo).

**Precedence, by evidence** — the user-level file was moved aside and restored under a fail-safe procedure: backup **outside the repo** first, an `EXIT`/`INT`/`TERM` **trap** to restore it, and a post-restore check.

| state | over-ceiling NLP probe (1,500 rows, `NLP=CONOPT`) |
|---|---|
| user-level file **present** | solves — `MODEL STATUS 1 Optimal` |
| user-level file **absent** | **refused** — `exceeds the demo license limits` (the system-directory demo becomes effective) |
| user-level file **restored** | solves — `MODEL STATUS 1 Optimal`; **restored file byte-identical** to its pre-test SHA-256 |

**Finding:** the **user-level file takes precedence**; the system-directory demo is the **fallback**. Every pipeline invocation (same binary, same user and `HOME`) reads the user-level license. A process with a different `HOME` or user would silently fall back to the demo — see §6.

## 2. Per-solver probes — each above its own demo ceiling (Unknown 1.1)

One scalable synthetic model per type (`set i /1*N/`, one constraint per element), run with the pipeline's own solver options. Demo runs use `license=` pointed at the system-directory demo file — **nothing is displaced**. Each type was also run just **under** its ceiling on the demo, to show size is what flips the result.

| type | options | under ceiling, demo | **above ceiling, demo** | above ceiling, effective license |
|---|---|---|---|---|
| LP (1,500 / **2,500**) | `LP=CPLEX` | solves (CPLEX, MS 1) | **refused** | **CPLEX** · SOLVER STATUS 1 · MODEL STATUS 1 Optimal |
| NLP (900 / **1,500**) | `NLP=CONOPT` | solves (CONOPT, MS 1) | **refused** | **CONOPT** · SOLVER STATUS 1 · MODEL STATUS 1 Optimal |
| QCP (900 / **1,500**) | `NLP=CONOPT` (as `verify_convexity.py` passes it) | solves (CONOPT, MS 2) | **refused** | **CONOPT** · SOLVER STATUS 1 · MODEL STATUS 2 Locally Optimal |
| MCP (900 / **1,500**) | — | solves (PATH, MS 1) | **refused** | **PATH** · SOLVER STATUS 1 · MODEL STATUS 1 Optimal |

**The positive control — the demo refusals, verbatim** (GAMS's own lines; they also state the ceilings):

```
LP : **** The model exceeds the demo license limits for linear models of more than 2000 rows or columns
NLP: **** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns
QCP: **** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns
MCP: **** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns
```

**Finding:** the effective license lifts the limit on **all four solver paths the pipeline uses — CPLEX (LP), CONOPT (NLP), the QCP solver and PATH (MCP)**. No split by solver. The **QCP solver actually used is CONOPT**: `verify_convexity.py`'s `NLP=CONOPT` does not select it, CONOPT is simply this install's default QCP solver (measured 2026-10-12: `NLP=IPOPT` still ran CONOPT, `QCP=IPOPT` ran IPOPT) — so `emfl`'s path is CONOPT today, but would change silently if the default changed. Ceilings: **2,000** rows or columns for linear models, **1,000** for nonlinear (QCP and MCP count as nonlinear).

## 3. Edition discriminator for `.lst` files (Unknown 1.2)

`.lst` headers do **not** carry the license block (that goes to the GAMS log), but every listing carries markers that distinguish the editions. The classifier uses only generic GAMS text; the licensed `USER:` line names the licensee, so it is matched **by prefix only, via a negative lookahead, and never captured**:

```python
DEMO_RE = re.compile(r"^(?:\*{4} The model exceeds the demo license limits\b|USER: GAMS Demo,)", re.M)
LIC_RE  = re.compile(r"^USER: (?!GAMS Demo,)", re.M)
# demo if DEMO_RE matches; else licensed if LIC_RE matches; else None (unknown — never guessed)
```

A refused demo run has **no** `USER:` line (it stops before the solve) but always has the refusal line; a completed demo run has `USER: GAMS Demo, …`; a completed licensed run has a `USER:` line that is not `GAMS Demo,`. A listing matching neither (e.g. aborted before the header) is classified `None` — matching the schema's null semantics (Task 5).

**Classification of every paired listing** (each pair: same model, demo vs effective license):

| listing | stage | expected | classified |
|---|---|---|---|
| LP probe, above ceiling | demo refused / licensed | demo / licensed | ✅ demo / ✅ licensed |
| LP probe, under ceiling (demo) | completed | demo | ✅ demo |
| NLP probe, above / under | demo refused, licensed / demo completed | demo, licensed / demo | ✅ ✅ / ✅ |
| QCP probe, above / under | demo refused, licensed / demo completed | demo, licensed / demo | ✅ ✅ / ✅ |
| MCP probe, above / under | demo refused, licensed / demo completed | demo, licensed / demo | ✅ ✅ / ✅ |
| **convexity stage** — `trnsport.gms` with `LP=CPLEX` (as `verify_convexity.py`) | demo / licensed | demo / licensed | ✅ / ✅ |
| **MCP stage** — `trnsport_mcp.gms` golden | demo / licensed | demo / licensed | ✅ / ✅ |
| **presolve stage** — `mingamma_mcp_presolve.gms` golden (one listing holding an NLP **and** an MCP solve; run in a throwaway worktree, `cwd` at its root) | demo / licensed | demo / licensed | ✅ / ✅ |
| precedence test — user file absent / restored | demo / licensed | demo / licensed | ✅ / ✅ |

**20 / 20 classified correctly. Inverted control:** swapping the classifier's two outputs yields **20 / 20 mismatches** and a non-zero exit — the check can fail, so its pass means something.

## 4. License-neutrality sample (Unknown 1.5)

**Sample, by identity, from candidates outside both gated populations** (131 of the 142; deterministic: within each stratum, sorted by recorded translate time, translates over 60 s dropped, evenly spaced picks):

| stratum | models |
|---|---|
| cold match (`model_optimal` + match) | `rbrock`, `house`, `pindyck`, `prolog`, `cesam2` |
| presolve match (`model_optimal_presolve` + match) | `mingamma`, `himmel16`, `harker`, `moncge`, `catmix` |
| solved, mismatch | `weapons` |
| `model_infeasible` | `agreste` |
| `path_syntax_error` | `indus` *(this stratum's members all translate in > 60 s; the 60 s filter was relaxed and its fastest member taken, rather than dropping the stratum)* |

*Excluded: the 7 candidates with no `mcp_solve` record — they never reach GAMS, so the license cannot affect them.*

**Procedure:** each model run through the real pipeline (`run_full_test.py --model <id>`) in a **throwaway worktree** (`cwd` at its root, as the pipeline requires), with the retention patch (`artifacts/RETENTION_PATCH.md`) applied so **every GAMS invocation's own listing** was classified; the worktree DB rows were then diffed against the committed (demo-era) rows on outcome, objective (relative tolerance 1e-6) and comparison verdict. An `EXIT` trap removed the worktree and the retained listings.

**Edition of every invocation:** **20 / 20 licensed** (13 cold `<id>_mcp` solves + 7 presolve retries), all from `head_sha` `35b296b3`.

**Diff: 0 of 13 rows changed** — every outcome, objective and verdict identical (e.g. `house` `model_optimal / 4500.0 / match`, `weapons` `model_optimal / 1700.397 / mismatch`, `agreste` `model_infeasible / 3501.634 / not_tested`, `indus` `path_syntax_error / None / not_tested`).

**Positive control (synthetic — never a real gated model):** the **same** diff function applied to the synthetic over-ceiling NLP probe, demo vs effective license, reports **`outcome: license_refused → model_status_1; objective: None → 1500.0`** — so a clean diff on the sample is not vacuous.

**Finding:** **sample-neutral at `35b296b3`.** A sample cannot establish the universal claim; it is **routed to the sprint's first licensed full run**, whose license-neutrality is a `PROJECT_PLAN.md` Sprint 40 gate.

## 5. Recommendation — replace the system-directory demo file (owner action)

**Recommended: yes.** The pipeline is licensed today only because it runs as the user whose `HOME` holds the user-level file. Any invocation with a different user or `HOME` (a `sudo` run, a launch agent, a container or CI-like environment, another account) silently falls back to the **2026-07-13 demo** in the system directory — and a demo run of an under-ceiling model succeeds normally, so nothing announces it. Copying the full license over `…/Versions/54/Resources/gamslice.txt` (keeping the demo as a backup outside the install) removes that silent fallback on this machine. Two cautions: a GAMS upgrade or reinstall can overwrite the system-directory file again, and this does nothing for CI (Task 4) — which is why Task 5's per-row `license_edition` stamp is still needed: it detects a demo run after the fact, wherever it happens.

## 6. Operational facts for Task 4

- **Effective license path:** `~/Library/Application Support/GAMS/gamslice.txt` (user level); demo fallback at `/Library/Frameworks/GAMS.framework/Versions/54/Resources/gamslice.txt`.
- **Edition:** evaluation license, **expires 2027-09-21**.
- **Node-locking evidence (described, not quoted):** the license header GAMS prints at run time carries a **node identifier** together with **memory and core-count fields** — the shape of a license bound to this machine.
- **Multiple machines / hosted runners:** **not determinable from the file.** The node field suggests it will not validate on a fresh GitHub-hosted runner; whether the terms allow a second machine (or a dedicated runner) is an **owner question for GAMS** — carried to Task 4's assessment and Task 6's decision 3.
