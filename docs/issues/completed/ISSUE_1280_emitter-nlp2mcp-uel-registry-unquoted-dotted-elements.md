# Emitter: `nlp2mcp_uel_registry` Emits Unquoted UELs With Dots

**GitHub Issue:** [#1280](https://github.com/jeffreyhorn/nlp2mcp/issues/1280)
**Status:** RESOLVED — fixed 2026-04-30 (the emitter fix had landed in an earlier commit; this PR refreshes the stale checked-in `mathopt4_mcp.gms` artifact and adds an integration regression test).
**Severity:** Medium — Compile-time syntax error risk depending on GAMS version; silent misinterpretation risk otherwise
**Date:** 2026-04-19
**Last Updated:** 2026-04-30
**Affected Models:** `mathopt4` (observed); any model whose symbol set feeds the UEL registry with attribute-access forms (`<sym>.<attr>`)
**Labels:** `sprint-25`

---

## Problem Summary

In `data/gamslib/mcp/mathopt4_mcp.gms` line ~28, the `nlp2mcp_uel_registry` set is declared with unquoted elements that contain `.` characters:

```gams
Set nlp2mcp_uel_registry /
    x1.l,
    x2.l,
    ...
/;
```

GAMS UELs containing punctuation (dots, hyphens, spaces) must be **single-quoted** — `'x1.l'`. Unquoted, the compiler either:

- **Rejects the declaration** with a syntax error (common on newer GAMS versions);
- **Silently truncates** at the dot (older versions), producing a UEL `x1` rather than `x1.l` and confusing downstream attribute lookups.

Both outcomes are incorrect. The emitter must quote every UEL unconditionally (safest) or conditionally when the element string contains non-identifier characters.

---

## Reproduction

```bash
grep -n "nlp2mcp_uel_registry\|x1\.l\|x2\.l" data/gamslib/mcp/mathopt4_mcp.gms | head -10
```

Expected after fix:

```gams
Set nlp2mcp_uel_registry /
    'x1.l',
    'x2.l',
    ...
/;
```

## Why `mathopt4`?

`mathopt4` happens to exercise a code path where the UEL registry is populated from pre-solve attribute accesses (e.g., for seeding initial `.l` values). Other models go through a different registry population path that uses plain identifiers. The bug is structural in the emitter but only triggers on the subset of models whose translations invoke the attribute-form registry entries.

Audit task for the fix: check which other model outputs in `data/gamslib/mcp/` contain unquoted dotted UELs in any `Set` declaration.

---

## Suggested Fix

In the emitter that writes the `nlp2mcp_uel_registry` set declaration (likely under `src/emit/*.py`):

1. Wrap every UEL element in single quotes unconditionally. GAMS accepts `'foo'` identically to `foo` for plain identifiers, so there's no downside.
2. If an element itself contains a single quote, escape it as `''` (standard GAMS quoting).

```python
def _emit_uel(name: str) -> str:
    return "'" + name.replace("'", "''") + "'"
```

## Regression Guards

After fix:

- Recompile `mathopt4_mcp.gms` with GAMS compile-check; syntax errors on `x1.l`/`x2.l` must disappear.
- Golden-file diff: every other model's `nlp2mcp_uel_registry` elements should now be quoted; the diff against the pre-fix output should be exactly that quoting delta and nothing else.

---

## References

- PR #1273 review comment #3107085385
- Sibling Sprint 25 issues: #1275–#1279

## Estimated Effort

1–2 hours (locate emitter site + add unconditional quoting + GAMS compile-check regression).

---

## Files Involved

- `src/emit/*.py` — `nlp2mcp_uel_registry` declaration emission
- `tests/unit/emit/` — new test asserting dotted UELs are quoted
- `data/gamslib/mcp/mathopt4_mcp.gms` — reference artifact (regenerated after fix)

---

## Resolution (2026-04-30)

### What was found

The emitter-side fix had ALREADY landed in an earlier commit (the
`_sanitize_uel_element` helper at `src/emit/original_symbols.py:351` and
its application at `src/emit/emit_gams.py:1289`). Re-emitting
`data/gamslib/raw/mathopt4.gms` from the live emitter produces the
correctly-quoted form:

```gams
Set nlp2mcp_uel_registry / 'x1.l', 'x1_0', 'x2.l', 'x2_0' /;
```

However, the **checked-in artifact** (`data/gamslib/mcp/mathopt4_mcp.gms`)
was stale and still showed the unquoted form (`x1.l, x2.l`). It dated
from before the emitter fix landed and was never refreshed.

### What was changed

1. **Refreshed `data/gamslib/mcp/mathopt4_mcp.gms`** — re-emitted from
   the live emitter to mirror the fixed quoting behavior. 1-line diff:
   the registry declaration now reads
   `Set nlp2mcp_uel_registry / 'x1.l', 'x1_0', 'x2.l', 'x2_0' /;`.

2. **Added integration test** (`tests/integration/emit/test_mathopt4_uel_registry_quoting.py`)
   covering 2 cases:
   - Dotted attribute labels (`x1.l`, `x2.l`) are emitted single-quoted.
   - Plain labels (`x1_0`) are quoted but NOT double-quoted (`''x1_0''`).

### Audit (per the issue's audit task)

Searched all `data/gamslib/mcp/*.gms` artifacts for unquoted dotted
UELs. Only `mathopt4_mcp.gms` was affected; all other models'
`nlp2mcp_uel_registry` declarations were already correct (either no
dots, or already single-quoted).

### Verification

- **Buggy form** (`Set nlp2mcp_uel_registry / x1.l, x2.l /;`) — confirmed
  GAMS rejects with `$161 Conflicting dimensions in element` on the
  current GAMS 53.1.0 runtime.
- **Fixed form** (`Set nlp2mcp_uel_registry / 'x1.l', 'x2.l' /;`) —
  compiles cleanly, no syntax errors.
- Sanitizer unit test (`test_original_symbols.py:3324+`) covers
  `_sanitize_uel_element` directly.
- New integration test verifies the emitter calls the sanitizer
  correctly end-to-end on the `mathopt4` corpus.
- Quality gate clean: `make typecheck && make lint && make format &&
  make test` (**4,677 passed**, 10 skipped, 1 xfailed).
