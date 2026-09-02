# Epic-5 scoping measurement scripts

`cge_scan.py` produces **every corpus figure** in `../CGE_DEGENERACY_SCOPING.md`
§6–§7 (Sprint 39 Prep Task 10), including the fixed-price / numéraire column.
Committed so the survey is reproducible from the repo rather than from prose.

**Analysis only.** It parses each model to IR and records structural signals. It
**solves nothing**, and in particular runs **no camcge experiment** — the banned
variants in §4a stay banned.

Run from the repo root; writes `$OUT/cge_scan.json` (default `/tmp/s39t10`).
**~45 minutes** for the full 219-model corpus; **41 models do not parse**, so
every figure derived from it is a **lower bound**.

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

**The blind spot was not a camcge quirk.** Over the 178 parsed models the two
probes disagree on **6**: `camcge`, `glider`, `korcge`, `orani`, `otpop`,
`robot`. On `camcge` they read `["pwm"]` vs `[]`; on `orani`, `["phi","pm"]` vs
`["pm"]` — the incomplete probe found one of two fixes and looked like it had
worked.

Verified 2026-09-02 at `365a538a`: a full re-run of this script reproduces the
published §6.1 column for all nine CGE-shaped models.
