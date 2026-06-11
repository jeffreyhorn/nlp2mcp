# Priority 8 — Golden-Staleness Drift Audit + CI-Check Design (PR26)

**Task:** Sprint 28 Prep Task 7 (the audit *ran* the current emit; the check + CI job are *built* in-sprint)
**Date:** 2026-06-11
**Deliverable script (to be built):** `scripts/sprint_audit/check_golden_staleness.py`
**Purpose:** Catalog the current golden drift, define the allowlist, and design the regenerate→diff→report check + its CI gate + the `make regen-goldens` bulk-refresh target — so the silent golden drift that recurred across Sprint 27 (cesam/fawley/korcge/dinam noise in unrelated PRs) is caught automatically.

**Audit method:** regenerate every committed golden via the canonical pipeline emit — `python -m src.cli <raw> -o <out> --quiet` (plus `--nlp-presolve` for `*_mcp_presolve.gms`), the exact command `scripts/gamslib/batch_translate.translate_single_model` uses — and byte-diff against the committed artifact. 164 goldens audited (153 `*_mcp.gms` + 11 `*_mcp_presolve.gms`).

---

## 1. Drift Inventory (Unknown 8.1)

| Class | Count | Models |
|---|---|---|
| **CLEAN** (regen == committed) | **154** | all `*_mcp.gms` except the allowlist; all `*_mcp_presolve.gms` except the 4 below |
| **DRIFTED** (regen != committed) | **4** | `camshape_mcp_presolve.gms`, `cesam_mcp_presolve.gms`, `fawley_mcp_presolve.gms`, `korcge_mcp_presolve.gms` — **all presolve variants** |
| **Allowlist** (emit out-of-scope) | **6** | danwolfe, decomp, saras (multi-solve driver scripts); nemhaus, nonsharp, trnspwl (discrete MIP) |
| **Total** | 164 | |

### The 4 drifted goldens (the refresh-commit scope)

All four are `*_mcp_presolve.gms` variants — the plain `*_mcp.gms` goldens are **100% clean**. The presolve goldens drifted because Sprint 27 deliberately did **not** sweep them during checkpoints ("measure, don't sweep" — `SPRINT_LOG.md` Day 10 "reverted incidental retest golden regens camshape/fawley/otpop `_mcp_presolve`"), so they lag the current emit.

| Golden | Changed lines | Likely cause |
|---|---|---|
| `camshape_mcp_presolve.gms` | 7 (415→408) | #1424 subset-default fix (Sprint 27 Day 11) — presolve variant not regenerated |
| `cesam_mcp_presolve.gms` | 128 (378→350) | Sprint 27 Day-4 cesam2 bug-class fixes touched cesam emit |
| `fawley_mcp_presolve.gms` | 22 (378→380) | #1356 comp_up subset-narrowing (Sprint 27 Day 5) |
| `korcge_mcp_presolve.gms` | 247 (704→625) | #1424 subset-default + Pattern-C changes; large CGE emit |

These are **real corrections** (current emit is the source of truth; the committed goldens are stale), not regressions — confirmed by the determinism check (§3) and by their plain `*_mcp.gms` siblings being clean.

### Slow-emit models (a CI-runtime concern, not drift)

Eight in-scope translating models needed > 240 s to emit (re-classified at a 900 s timeout — **all CLEAN**): clearlak, dinam, ferts, ganges, gangesx, indus, tabora, turkpow. ganges/gangesx are the slowest (~minutes each). They are not drifted; they are the **runtime budget driver** for the CI check (§4 / Unknown 8.2).

---

## 2. Allowlist (Unknown 8.1)

Models the check **excludes** from the staleness gate, with a reason per entry. These have committed goldens (historical artifacts from when they last emitted) but the current emit no longer produces them, so diffing is meaningless.

| Model | Type | Reason | Excluded because |
|---|---|---|---|
| danwolfe | LP | multi-solve driver script (out of scope) | emit aborts: "Model is a multi-solve driver script and is out of scope for nlp2mcp" |
| decomp | LP | multi-solve driver script | same |
| saras | NLP | multi-solve driver script | same |
| nemhaus | MIP | discrete (MIP/MINLP) — out of scope | emit aborts: "Model is discrete … out of scope" |
| nonsharp | MIP | discrete | same |
| trnspwl | MIP | discrete | same |

**No non-deterministic models** were found (§3) — the allowlist is purely the 6 out-of-scope models. The allowlist is data-driven: a model belongs on it iff `python -m src.cli` exits non-zero with an out-of-scope diagnostic. The translate-failure models with **no committed golden** (iswnm, mexls, nebrazil, sarf) are not in the audit set and need no allowlist entry.

---

## 3. Determinism (Unknown 8.3)

Regeneration is **determinism-clean** under the PR12 guard. Spot-check: 8 representative models (abel, trnsport, launch, qdemo7, cesam2, korcge, mine, camshape) regenerated under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=42` → **byte-identical for all 8**. This matches the Sprint 27 Day-13 full-pipeline PR12 result (byte-identical ×3 seeds). The check can therefore treat any regen≠committed diff as genuine drift, not seed noise.

---

## 4. Check Interface — `scripts/sprint_audit/check_golden_staleness.py`

```bash
# Report mode (default; CI uses this): regenerate every in-scope golden, diff, report
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py            # exit 1 if any non-allowlisted golden drifted
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py --models clearlak,dinam   # subset
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py --fix      # bulk refresh = rewrite drifted goldens in place (= make regen-goldens)
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py --json out.json
```

| Flag | Meaning |
|---|---|
| (none) | regenerate → byte-diff → report; **exit non-zero** if any non-allowlisted golden drifted; exit 0 if all clean/allowlisted |
| `--fix` | regenerate and **overwrite** the drifted goldens in place (the bulk refresh `make regen-goldens` wraps) |
| `--models <csv>` | restrict to a subset (for fast local checks / the changed-emit subset) |
| `--json <path>` | machine-readable drift report |

- **Allowlist** is loaded from a committed list (`scripts/sprint_audit/golden_staleness_allowlist.txt`, seeded with the 6 above); a model on it that emits successfully **and** drifts is reported as a warning (the allowlist may be stale), not a hard failure.
- **Determinism guard:** the report mode regenerates once; `--fix` additionally re-emits a second time and asserts byte-identity before overwriting (so a non-deterministic emit never silently churns a golden).
- Reuses `scripts.gamslib.batch_translate.translate_single_model` so the emit command stays identical to the pipeline.

### `make regen-goldens`

```makefile
regen-goldens:
	.venv/bin/python scripts/sprint_audit/check_golden_staleness.py --fix
```

A single command that refreshes every drifted golden — the reviewable bulk-refresh used for the one-time corpus refresh (§6) and after any intentional emit change.

---

## 5. CI Integration (Unknown 8.2)

A `.github/workflows/golden-staleness.yml` job, modeled on `pr19-emit-solve-validation.yml`:

```yaml
on:
  pull_request:
    branches: [main]
    paths:
      - "src/ad/**/*.py"
      - "src/kkt/**/*.py"
      - "src/emit/**/*.py"
      - "src/ir/**/*.py"
      - "scripts/sprint_audit/check_golden_staleness.py"
      - "scripts/sprint_audit/golden_staleness_allowlist.txt"
      - ".github/workflows/golden-staleness.yml"
```

- **Job:** run `check_golden_staleness.py` (report mode) → fail the PR if any non-allowlisted golden drifted, with a failure message listing the drifted models + the `make regen-goldens` remedy.
- **Runtime budget / the > 5 min friction threshold:** a full-corpus emit-only regen (no solve) is dominated by the 8 slow models (ganges/gangesx ~minutes each); serially that exceeds 5 min. **Mitigation:** the CI job regenerates in **parallel** (`ThreadPoolExecutor`, ~6 workers — the audit method here) so wall-clock is bounded by the slowest single model (~a few minutes), and excludes the allowlist. If even parallelized it approaches the 5-min threshold, fall back to the **changed-emit subset** (the PR19 target-list pattern — regen only goldens whose emit a given `src/` change can affect) on PRs, with a **nightly full sweep** (`nightly.yml`) as the safety net.
- **Failure message format:**

  ```
  Golden staleness: 2 golden(s) drifted from current emit.
    DRIFTED: cesam_mcp_presolve.gms (128 lines), korcge_mcp_presolve.gms (247 lines)
  Run `make regen-goldens` and commit the refreshed goldens (or, if unintended, fix the emit).
  ```

---

## 6. One-Time Corpus-Refresh Commit Scope (Unknown 8.1)

A single reviewable commit, **separate from any fix**, regenerating exactly the 4 drifted presolve goldens:

```bash
make regen-goldens     # rewrites the 4 drifted *_mcp_presolve.gms; the 154 clean goldens are untouched
git add data/gamslib/mcp/camshape_mcp_presolve.gms \
        data/gamslib/mcp/cesam_mcp_presolve.gms \
        data/gamslib/mcp/fawley_mcp_presolve.gms \
        data/gamslib/mcp/korcge_mcp_presolve.gms
```

Scope: **4 files** (all presolve variants). The refresh is small and bounded because the plain `*_mcp.gms` corpus is already clean — the drift is confined to the presolve goldens Sprint 27 chose not to sweep. Land this as the first in-sprint commit (Day 0/1) so the CI gate starts from a clean baseline.

## 7. Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md && echo present
grep -Ei 'cesam|fawley|korcge|dinam' docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md
grep -Ei 'allowlist|\.github/workflows|regen-goldens' docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md
```
