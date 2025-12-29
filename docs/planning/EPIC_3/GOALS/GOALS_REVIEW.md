# EPIC 3 Goals Review

## Findings
- High — `docs/planning/EPIC_3/GOALS/GOALS_ORIG.md:75-118`: Convexity verification hinges on a solver reporting "optimal" with optional multi-solver checks; there is no mandatory use of global-capable solvers, multi-start, or structural convexity tests, so non-convex models can be mislabeled as "verified_convex," poisoning the corpus and downstream metrics.
- Medium — `docs/planning/EPIC_3/GOALS/GOALS_ORIG.md:80-117,172-180,242-250`: The plan compares MCP solutions to "original NLP solution" but the database schema only retains objective/time and not the primal/dual vectors (or a persisted baseline solution file), which makes later equality checks and regression tracking under-specified and potentially irreproducible.
- Medium — `docs/planning/EPIC_3/GOALS/GOALS_ORIG.md:131-212`: The JSON schema omits key provenance (GAMS version, solver versions/options, platform, random seeds, license tier) and run configuration, so reported success rates may be non-reproducible across machines and licenses; this undercuts the stated goal that any developer can re-run locally and match results.
- Medium — `docs/planning/EPIC_3/GOALS/GOALS_ORIG.md:36-66,596-604`: Discovery/filtering relies on GAMSLIB metadata to exclude IP/MPEC/etc. but does not require static checks for integer variables, complementarity sections, or external data includes, nor a clear skip/record path for models with missing dependencies; risk is that ineligible or partially-downloaded models enter the "convex corpus" and distort metrics.
- Low — `docs/planning/EPIC_3/GOALS/GOALS_ORIG.md:216-263`: Pipeline scripts record timing/errors but do not plan for deterministic reruns (e.g., fixed seeds, capped threads, consistent PATH options), which may cause noisy pass/fail status updates in the database and complicate progress comparisons.

## Questions / Clarifications
- Resolved: Use a global-capable solver for convexity certification; if only a local optimum is reported, tag the model as possibly non-convex (do not mark `verified_convex`).
- Resolved: Persist full NLP solution artifacts (variable/multiplier vectors and solver logs) per model to make MCP-vs-NLP comparisons reproducible and audit friendly.
- Resolved: Handle includes/external data (download/resolve dependencies); if a model is mixed discrete/continuous, label it discrete/mixed and skip parse/translate/solve.
