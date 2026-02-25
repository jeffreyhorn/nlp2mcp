# Cesam2: Alias Domain Resolution Failure During Translation

**GitHub Issue:** [#858](https://github.com/jeffreyhorn/nlp2mcp/issues/858)
**Status:** FIXED
**Severity:** Medium — Model parses but fails at translate stage
**Date:** 2026-02-24
**Affected Models:** cesam2

---

## Problem Summary

The cesam2 model parses successfully but fails during translation when the AD/index
mapping module tries to enumerate equation instances for `ASAMEQ(ii,jj)` and cannot
resolve the domain set `jj` because it is an alias for `ii` (a dynamic subset of `i`
with no concrete members at build time).

---

## Root Cause

`_resolve_alias()` in `src/ad/index_mapping.py` looked up the target set's members
directly but did not apply the dynamic subset fallback (Issue #723) when the target
set had no members. So alias `jj` → set `ii` (domain `i`, 0 members) returned an
empty list, causing the downstream "no members" error.

---

## Fix Applied

Added dynamic subset fallback logic to `_resolve_alias()`: when the target set has
no static members but has a parent domain, fall back to the parent set's members
(same pattern as the Issue #723 fallback in `resolve_set_members()`).

**Note:** cesam2 now progresses past this error but fails later with
`diff_unsupported_func` (SetMembershipTest condition evaluation + centropy
differentiation). That is a separate issue.

---

## Files Changed

| File | Change |
|------|--------|
| `src/ad/index_mapping.py` | Added dynamic subset fallback in `_resolve_alias()` for alias targets with no members |

---

## Related Issues

- **Issue #817** (completed): Previous cesam2 blocker (conditional assignment in loop parsing)
- This is a **separate, downstream** issue from #817; cesam2 now parses but fails at translate
