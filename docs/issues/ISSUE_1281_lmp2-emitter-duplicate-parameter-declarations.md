# lmp2: Emitter Redeclares `Parameter A/b/cc` After Original Declaration (Symbol Redefinition)

**GitHub Issue:** [#1281](https://github.com/jeffreyhorn/nlp2mcp/issues/1281)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** High — Likely proximate cause of `lmp2`'s current `path_solve_terminated` (GAMS rejects MCP at compile time)
**Date:** 2026-04-19
**Last Updated:** 2026-04-19
**Affected Models:** `lmp2` (observed); any model where the emitter inlines the original NLP source AND then regenerates Parameter declarations for the same symbols
**Labels:** `sprint-25`

---

## Problem Summary

In `data/gamslib/mcp/lmp2_mcp.gms` around line 53, the generated MCP re-emits:

```gams
Parameter A(mm,nn);
Parameter b(mm);
Parameter cc(p,nn);
```

for symbols that were **already declared** earlier in the same file via the emitter's inlined copy of the original NLP source. GAMS identifiers are case-insensitive, so the second `Parameter A(mm,nn)` is a symbol-redefinition compile error.

This is the suspected proximate cause of `lmp2`'s current pipeline state:

- `mcp_solve.status = "failure"`
- `mcp_solve.outcome_category = "path_solve_terminated"`
- `mcp_solve.error.message = "Parse error: no_solve_summary"`

The `no_solve_summary` result means GAMS rejected the MCP at compile time and never produced a `.lst` with a solve summary — consistent with a redefinition error aborting compilation.

---

## Reproduction

```bash
# Count duplicate declarations
grep -cnE "^Parameter\s+(A|b|cc)\b" data/gamslib/mcp/lmp2_mcp.gms
# → expect 2 hits per symbol (inlined original + regenerated)

# Confirm compile failure
gams data/gamslib/mcp/lmp2_mcp.gms lo=2 2>&1 | grep -E "\\*\\*\\*\\*.*redefin|already declared"
```

---

## Likely Root Cause

The emitter's parameter-emission pass doesn't check whether a parameter is already declared by the inlined original source. For the class of models where `src.cli` inlines the NLP body (instead of referencing it via `$include`), parameters declared inside that inlined block need to be excluded from the emitter's own regenerated declaration list.

Candidate code sites to audit:

- **`src/emit/original_symbols.py`** — handles inlining vs regenerating symbol declarations; most likely site for the dedup gap
- **`src/ir/parser.py`** / **`src/ir/preprocessor.py`** — may be where the parameter-name set feeding the emitter is computed (a missing "already declared in inlined source" set on the IR could also be the bug)

---

## Suggested Fix

1. Identify the emitter site that emits `Parameter <name>(...)` declarations during final MCP generation.
2. Cross-check each candidate name against the inlined original's symbol table. If already declared inline, skip the regeneration (or emit a single-line comment like `* Parameter <name>: already declared above by inlined source`).
3. Decide policy for cases where the emitter NEEDS to re-declare (e.g., if the original declaration was conditional): either extract the declaration out of the inline or leave it untouched and not re-emit.

Two implementation candidates:

- **Per-symbol dedup (minimal)**: maintain a `declared_symbols: set[str]` as the emitter walks the inlined body; skip any regeneration that collides.
- **Phase separation (cleaner)**: if the emitter has a clear "regenerate declarations" phase, feed it the IR's known-already-declared set up-front so it never considers those names.

---

## Regression Guards

After fix:

- `lmp2` pipeline: compile error must disappear; solve outcome should change from `path_solve_terminated` / `"Parse error: no_solve_summary"` to something else (ideally `model_optimal` or at least a different, actionable failure mode).
- Existing-matching models (54 current matches on the 143-scope; dispatch canary) must not regress — verify no model loses a legitimate parameter declaration.
- Add a unit test asserting that `Parameter <name>` appears at most once per symbol in a fixture output.

---

## Scope

This issue is about the **emitter's duplicate declaration** only. The other known lmp2 issues are distinct root causes and are tracked separately:

- **#1243** — lmp2: runtime division by zero in `stat_y` at initial point (different failure mode, activates only after compile succeeds)
- **#810** — lmp2: solve inside doubly-nested loop not extracted (parser / IR issue)
- **#912, #952** (closed) — prior lmp2 parser / emission fixes

Fixing #1281 is likely a prerequisite to surfacing #1243's runtime behavior in practice (since currently GAMS can't get past the compile step).

---

## References

- PR #1273 review comment [#3107191692](https://github.com/jeffreyhorn/nlp2mcp/pull/1273#discussion_r3107191692)
- Sibling Sprint 25 issues: #1275 (emitter absolute paths), #1276 (emitter duplicate `.fx`), #1280 (emitter unquoted UELs)

---

## Estimated Effort

2–3 hours (identify emitter site + add dedup check + regression test on `lmp2` and a handful of other inline-original models).

---

## Files Involved

- `src/emit/original_symbols.py` (most likely)
- `src/ir/parser.py` / `src/ir/preprocessor.py` (may need to expose a "declared by inlined source" set)
- `tests/unit/emit/` — new dedup assertion
- `data/gamslib/mcp/lmp2_mcp.gms` — reference artifact (regenerated after fix)
- `data/gamslib/raw/lmp2.gms` — source model
