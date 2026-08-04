# Follow-ups from the CI GAMS 53.1.0 → 54.2.1 transition (Sprint 35 Day 6)

**Filed:** 2026-08-03 · **Context:** the pinned CI GAMS demo 53.1.0 license expired ~2026-07-29, forcing a bump to 54.2.1 (`pr19-emit-solve-validation.yml`, `presolve-divergence.yml`; local resolvers in `test_solve.py`/`kkt_residual.py`/`test_nlp_presolve.py`). The bump is correct and necessary, but GAMS 54 is **stricter and does not solve identically to 53** on several models. Two items are deferred out of the Day-6 turkey PR (#1620) and tracked here.

---

## Follow-up 1 — robustlp NA matrix coefficients (allowlisted, needs a real fix)

**Symptom:** under GAMS 54 the robustlp MCP solve aborts with **EXECERROR = 84**, "**Matrix error — coefficient in variable below is NA**" (×9). Reproduced locally on the committed `data/gamslib/mcp/robustlp_mcp_presolve.gms` golden. GAMS 53 tolerated the NA coefficients; GAMS 54's matrix generation rejects them.

**Root class:** the robustlp MCP Jacobian carries **NA coefficients** — the #1322 NA-propagation class (a division/arithmetic producing NA that flows into the emitted matrix). The emit is **unchanged** by the turkey PR; this is a pre-existing latent fragility the version bump exposed.

**Interim action (Day 6):** `robustlp` added to `scripts/diagnostics/presolve_divergence_allowlist.txt` (DIVERGED → WARN), mirroring `korcge`. This unblocks the presolve-divergence gate while still surfacing the divergence as a WARN.

**The real fix (deferred):** eliminate the NA coefficients in robustlp's emitted MCP (trace which term goes NA — likely an NA-cleanup gap of the #1322 family). When fixed, **remove `robustlp` from the allowlist**. A candidate is the `emit_post_assignment_na_cleanup` family (`src/emit/original_symbols.py`) not covering the offending robustlp param, but that is a hypothesis to trace, not a confirmed surface.

---

## Follow-up 2 — v53 → v54 baseline review (does the KPI baseline hold under 54?)

**Observation:** the same presolve-divergence run under GAMS 54 reported **5 OBJ-GAPs** (info-only, non-failing): agreste, cesam, chain, fawley, rocket — embedded-vs-reference objective differences (non-convex models reaching different local optima). Whether these gaps are *new under 54* or pre-existing under 53 is unconfirmed, but combined with the robustlp abort they show **GAMS 54's solve behavior differs from 53's** on multiple models.

**Why it matters:** the entire KPI baseline — **Solve 108 / Match 93 / genuine floor 75** and the committed `gamslib_status.json` DB — was established under **GAMS 53** (the licensed testbed). Now that:
- CI validates under GAMS 54, and
- local solve-verification (Day 6 test-infra fix) uses the newest installed version (54),

a re-solve under 54 could shift buckets (a borderline model moving `model_optimal` ↔ `model_optimal_presolve` ↔ `model_infeasible`, or a match ↔ mismatch), which would change the headline figures.

**Deferred question for a dedicated review (before/at the Day-13 retest):**
1. Re-solve the corpus under GAMS 54 in the licensed testbed and diff the buckets vs the v53-built DB. Are 108/93/75 preserved?
2. If buckets shift, decide the canonical validation version (pin the DB to 54 and re-baseline, or keep 53 for solving where a license is available).
3. Confirm the PR19 Tier-0/1 canaries stay green under 54 (small convex models — expected stable, but this is the first 54 CI validation).
4. Re-check the 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket) — are the gaps benign local-optima differences or a real regression?

**Owner/timing:** the Day-13 retest is the natural checkpoint (it re-solves under ≥3 `PYTHONHASHSEED`); this transition adds a **GAMS-version axis** to that retest. Flag in the Sprint-35 close + carry to Sprint 36 if unresolved.

---

## Follow-up 3 — markov `slow` integration test failing on main (surfaced Day 9)

**Symptom:** `tests/integration/kkt/test_markov_multi_pattern.py::TestMarkovMultiPatternIntegration::test_markov_stationarity_has_correction_term` **fails on clean main** (Day-9 fawley src/ attempt fully reverted; helper absent, `git diff main -- src/` empty).

**The failure is a sum-shape + nu-indexing mismatch, not merely a `'1 -'` substring.** The test asserts three things about the freshly-emitted `stat_z`, in order: (a) `nu_constr(s,i)` appears (a *direct*, non-summed diagonal correction term); (b) an off-diagonal sum matches `sum(...) * nu_constr(s__kkt1,...)`; (c) that sum's derivative contains no `1 -`/`1 +` Kronecker delta. Per the test docstring the intended **post-fix** first term is `sum((s__kkt1,j), (-b*pi(...)) * nu_constr(s__kkt1,j)) + nu_constr(s,i)` — a separate diagonal term plus an off-diagonal sum. But the current emit's first sum-term is:

```
sum((s__kkt1,j), ((1 - b * pi(s,i,s,i,s__kkt1)) * nu_constr(s,i))$(sp(s) and j(i)))
```

which matches **neither** the pre-fix form (`... * nu_constr(s__kkt1,j)`) **nor** the intended post-fix form: it retains the `1 -` Kronecker **and** indexes `nu_constr` by the *outer* `(s,i)` rather than the *summed* `(s__kkt1,j)`. Assertion (a) passes only trivially (the `nu_constr(s,i)` it finds is *inside* the sum, not the intended direct correction term); the `1 -`/off-diagonal check (c) is what reports, but the deeper defect is that the #1110 markov multi-pattern correction (diagonal term split out of the off-diagonal sum) is **absent** from the current emit. (Committed `data/gamslib/mcp/markov_mcp.gms:162` shows the same first term — the golden agrees with the fresh emit; the divergence is against the *test's intended* shape, not against the golden.)

**Why it went unseen:** the module is marked `pytest.mark.slow` (line 17), so `make test` (`-m "not slow"`) **excludes** it — Day-6's full `make test` was green (5040/0) with this test never run. It surfaced only because the Day-9 KKT run filtered on `stationarity` (matching the test name) without the slow exclusion.

**Not the fawley work:** fails with the fawley helper reverted; the fawley attempt separately *added* a `sameas(j,i)` to markov, but the first-sum shape defect above is present either way. This is **pre-existing and independent**.

**Deferred question (Day-13 triage):** did the markov #1110 multi-pattern correction **regress** (a later shared-`_add_indexed_jacobian_terms` change collapsed the split-out diagonal term back into the sum and re-mangled the nu-indexing to `(s,i)`), or was the test's intended post-fix shape never actually the emitted form? Bisect for the last commit where this test was green (`git log` the `slow` module + `-p data/gamslib/mcp/markov_mcp.gms` around `stat_z`), then decide: fix the emit (restore the split diagonal term + `nu_constr(s__kkt1,j)` indexing), or — if the current shape is provably correct — update the assertion. Either way the `slow` marker is hiding it from `make test`; consider un-marking (or a fast unit-level shape guard) once resolved.

---

**Document Status:** 🔵 Open follow-ups (1–2 from PR #1620; 3 from the Day-9 fawley attempt, sharpened Day 10)
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team
