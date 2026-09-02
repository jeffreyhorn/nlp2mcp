# Epic-5 scoping measurement scripts

`cge_scan.py` produced every corpus figure in `../CGE_DEGENERACY_SCOPING.md` §6–§7
(Sprint 39 Prep Task 10). Committed so the survey is reproducible from the repo.

**Analysis only.** It parses each model to IR and records structural signals. It
**solves nothing**, and in particular it runs **no camcge experiment** — the
banned variants in §4a stay banned.

Run from the repo root; writes `$OUT/cge_scan.json` (default `/tmp/s39t10`).
**~45 minutes** for the full 219-model corpus; 41 models do not parse, so every
figure derived from it is a **lower bound**.

⚠ **Its `fixed_prices` field is known-incomplete and is not used for any published
figure.** It probes `fx` / `fx_map` only, and a GAMS `pwm.fx(i) = pwm0(i)` lands in
**`fx_expr_map`** — so camcge reads as having no fixed price when it has one. The
published fixed-price column was re-derived with the corrected four-field probe
(`fx`, `fx_map`, `fx_expr`, `fx_expr_map`); see §7. The field is left in place
because the bug is part of the finding: a detector conjunct can be silently
inert, and here it was.
