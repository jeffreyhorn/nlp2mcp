# Epic-5 scoping measurement scripts

`cge_scan.py` produces **every corpus figure** in `../CGE_DEGENERACY_SCOPING.md`
§6–§7 (Sprint 39 Prep Task 10), including the fixed-price / numéraire column.
Committed so the survey is reproducible from the repo rather than from prose.

**Analysis only.** It parses each model to IR and records structural signals. It
**solves nothing**, and in particular runs **no camcge experiment** — the banned
variants in §4a stay banned.

⚠ **Prerequisite: the corpus is not in the repo.** `data/gamslib/raw/*.gms` is
**gitignored**, so a fresh checkout has none of it and the scan has nothing to
read. Populate it first with `scripts/download_gamslib_raw.sh` (219 `.gms`
files). The script now **exits non-zero with that instruction** rather than
printing `0 models` and writing an empty JSON, which is what it used to do.

Run from the repo root; writes `$OUT/cge_scan.json` (default `/tmp/s39t10`).
**~45 minutes** for the full 219-model corpus; **39 models do not parse** in a
clean run, so every figure derived from it is a **lower bound**.

## ⚠ Two fixed-price fields, on purpose

| field | probe | use |
|---|---|---|
| `fixed_prices` | `fx`, `fx_map`, `fx_expr`, `fx_expr_map` | **correct** — this is the published §6.1 column |
| `fixed_prices_fx_only` | `fx`, `fx_map` only | **incomplete** — kept so the trap is visible |

A GAMS `pwm.fx(i) = pwm0(i)` does **not** land in `fx` or `fx_map`; the
right-hand side is an expression, so it lands in **`fx_expr_map`**. The first
version of this script probed only the first two fields, so **camcge read as
having no fixed price when it has one** — and the D4 detector, whose whole
purpose is that conjunct, *appeared* to flag camcge correctly while the conjunct
did nothing (`../CGE_DEGENERACY_SCOPING.md` §7.2).

Emitting both fields means the output is self-consistent — the published column
is reproducible from this script alone — **and** the failure remains visible in
the data rather than only in prose.

**The blind spot was not a camcge quirk.** The two probes disagree on **5**
models: `camcge`, `glider`, `korcge`, `otpop`, `robot`. On `camcge` they read
`["pwm"]` vs `[]`; on `robot`, `["phi","phi_dot"]` vs `["phi_dot"]` — the
incomplete probe found one of two fixes and looked like it had worked.

⚠ **`fixed_prices_fx_only` uses `vd.fx is not None`, not `if vd.fx`.** A scalar
fix to `0.0` is falsey, and the original probe dropped it — so the field would
disagree with `fixed_prices` for **two unrelated reasons** and the comparison
would prove nothing. The two probes must differ in **exactly one dimension: the
field set**. Before this was corrected the count read 6 and included `orani`,
whose `phi` disagreed for the truthiness bug rather than the `fx_expr_map` one.

⚠ **The parsed count is load-dependent.** `iswnm`, `mexls` and `turkey` sit at
the 120 s per-model timeout; **five runs gave 176 / 178 / 179 / 180 / 180**, the
176 taken while `make test` was running. Quote a range, or state the load
conditions. The published figures are from the two most recent **clean runs,
which agree at 180 parsed / 39 not** — and the detector counts D1–D4 were
identical across both, so no conclusion depends on the flapping models.

Verified 2026-09-02: a full re-run of this script reproduces the published §6.1
column for all **ten** CGE-shaped models in the clean-run table.
