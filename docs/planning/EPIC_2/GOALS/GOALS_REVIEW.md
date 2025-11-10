# EPIC 2 Goals Review

## Findings

- **Sequence risks around GAMSLib validation** – Real-world model ingestion (Goal 3) is deferred until Sprint 7, yet the parser/syntax discoveries from those models will dictate much of the epic backlog. Without an early baseline, the convexity work in Sprint 6 may optimize for the wrong problems and nested min/max support (Goal 2.2) could be scoped too late to unblock library models (`docs/planning/EPIC_2/GOALS.md:118-214, 305-464`).
- **Nested min/max and maximize bug prioritization** – The maximize multiplier bug and nested min/max limitations block correctness for current users, but nested min/max is slated for Sprint 8 even though it shares the same reformulation surface area as the Sprint 6 work. Shipping both bug fixes in early sprints would reduce rework and rebuild confidence quicker (`docs/planning/EPIC_2/GOALS.md:147-214`).
- **Convexity detection scope vs effort** – Goal 1 bundles heuristics, AST classification, CLI flags, and documentation into a single sprint. That’s ambitious, especially if AST-based classification requires symbolic composition rules; without staged milestones there’s a risk of slipping and impacting downstream releases (`docs/planning/EPIC_2/GOALS.md:41-116`).
- **Aggressive simplification before full real-world telemetry** – Sprint 9’s aggressive simplification targets 20–30% derivative reduction, but the benchmark harness that proves value depends on GAMSLib conversion metrics that only stabilize late in Sprint 8. Without earlier performance telemetry, it will be hard to measure regressions or prioritize rules (`docs/planning/EPIC_2/GOALS.md:215-403, 517-603`).
- **UX polish reserved solely for Sprint 10** – User-experience goals (diagnostics, stats dashboard, progress indicators) are scheduled after all parser and simplification work. Given UX gaps surfaced in EPIC 1, deferring every improvement to a single sprint risks rushed implementation or cuts if upstream work slips (`docs/planning/EPIC_2/GOALS.md:404-515, 603-674`).
- **Success metrics lightly tied to release gating** – Parser coverage (80% of GAMSLib) and conversion success (60%) are defined globally but not incrementally per sprint, making it difficult to assess whether Sprint 7/8 deliverables actually move the needle toward v1.0 readiness (`docs/planning/EPIC_2/GOALS.md:675-736`).

## Recommendations

1. **Pull forward GAMSLib ingestion and instrumentation**
   - Allocate part of Sprint 6 to automate model download and start collecting parser error buckets so Sprint 6 already informs Sprint 7 priorities.
   - Maintain a running conversion dashboard from Sprint 6 onward to highlight progress and prevent late surprises.

2. **Bundle all high-severity bug fixes up front**
   - Tackle both the maximize-bound multiplier bug and nested min/max support in Sprint 6 (or 6–7) so correctness issues stop blocking users before new features land.
   - Leverage the same reformulation/test harness for both fixes to avoid duplicate plumbing.

3. **Stage convexity detection deliverables**
   - Split Goal 1 into two increments: Sprint 6 delivers heuristic warnings + CLI flags; Sprint 7/8 (time-permitting) adds AST-based classification.
   - Tie warnings to telemetry coming from GAMSLib runs to validate signal/noise before investing in deeper analysis.

4. **Introduce rolling performance/UX checkpoints**
   - Add lightweight UX tasks each sprint (e.g., better error copy when new parser features land) instead of deferring everything to Sprint 10.
   - Start capturing performance stats as soon as GAMSLib models run (Sprint 7) so aggressive simplification (Sprint 9) has baseline data.

5. **Define sprint-level KPIs toward success metrics**
   - e.g., Sprint 7: “20% of targeted GAMSLib models parse”, Sprint 8: “50% parse / 30% convert”, Sprint 9: “Performance dashboard automated”.
   - Use these checkpoints to decide whether scope adjustments (e.g., additional parser features vs simplification) are necessary.

6. **Consider an additional goal for automated regression enforcement**
   - As parser coverage expands, add CI hooks (PATH smoke tests, GAMSLib sampling, performance guardrails) so new syntax doesn’t regress existing functionality—this aligns with the Quality & Robustness theme but warrants explicit planning.
