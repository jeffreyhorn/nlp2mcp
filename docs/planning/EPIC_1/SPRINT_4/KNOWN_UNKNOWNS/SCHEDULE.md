# Sprint 4 Known Unknowns – Prep & Early Sprint Schedule

## Overview
- Total verification effort: **79 hours (~9.9 eight-hour days)** across 23 Known Unknowns.
- Pre-Sprint critical path (tasks due before Sprint 4 Day 1 while PATH access is pending): **26 hours (~3.3 days)**.
- Earliest safe Sprint 4 start: **after Prep Day 4**, once Tasks 1.1–2.3 are complete; Task 2.4 now waits on PATH availability.
- Remaining tasks are scheduled across Sprint Days 1–7, with all PATH-dependent work clustered at the end to accommodate potential licensing delays.

## Effort Estimates by Task
| ID | Task | Priority | Deadline | Est. Hours | Est. Days |
|----|------|----------|----------|------------|------------|
| 1.1 | $include semantics & preprocessing | High | Before Sprint 4 Day 1 | 4.0 | 0.50 |
| 1.2 | Table block syntax coverage | High | Before Sprint 4 Day 1 | 4.0 | 0.50 |
| 1.3 | Fixed variable (.fx) semantics | High | Before Sprint 4 Day 1 | 3.0 | 0.38 |
| 1.4 | Nested $include handling | Medium | Before Sprint 4 Day 1 | 1.5 | 0.19 |
| 1.5 | $include path resolution & security | Medium | Before Sprint 4 Day 1 | 1.5 | 0.19 |
| 2.1 | min() MCP reformulation | Critical | Before Sprint 4 Day 1 | 6.0 | 0.75 |
| 2.2 | max() MCP reformulation | Critical | Before Sprint 4 Day 1 | 3.0 | 0.38 |
| 2.3 | abs() smoothing strategy | Medium | Before Sprint 4 Day 1 | 3.0 | 0.38 |
| 2.4 | PATH compatibility for non-smooth reformulations | High | Before Sprint 4 Day 1 | 3.0 | 0.38 |
| 4.1 | Line breaking for GAMS emission | High | Sprint Day 2 | 3.0 | 0.38 |
| 6.1 | $include preprocessing vs ModelIR | High | Sprint Day 2 | 3.0 | 0.38 |
| 3.1 | Scaling algorithm selection | High | Sprint Day 3 | 5.0 | 0.62 |
| 3.2 | Decide scaling application point | High | Sprint Day 3 | 3.0 | 0.38 |
| 4.2 | Aux variable naming scheme | Critical | Sprint Day 3 | 4.0 | 0.50 |
| 4.3 | Aux constraints in Model declaration | High | Sprint Day 3 | 3.0 | 0.38 |
| 4.4 | Emit fixed variables in MCP | High | Sprint Day 4 | 4.0 | 0.50 |
| 6.2 | Fixed vars in KKT assembly | Critical | Sprint Day 4 | 4.0 | 0.50 |
| 6.4 | Aux vars & IndexMapping | Critical | Sprint Day 4 | 4.0 | 0.50 |
| 5.1 | PATH behavior on nonlinear MCPs | Critical | Sprint Day 5 | 5.0 | 0.62 |
| 6.3 | Scaling impact on tests | High | Sprint Day 6 | 3.0 | 0.38 |
| 5.2 | Recommend PATH options | Medium | Sprint Day 6 | 3.0 | 0.38 |
| 5.3 | PATH failure reporting | Medium | Sprint Day 6 | 4.0 | 0.50 |
| 5.4 | PATH initial point guidance | Low | Sprint Day 7 | 2.0 | 0.25 |

## Day-by-Day Plan (8-hour capacity per day)
### Prep Day 1
- `1.1` – $include preprocessing deep dive & prototype harness (4h)
- `2.1` – Begin min() reformulation research + draft auxiliary constraint plan (4h)

### Prep Day 2
- `2.1` – Complete min() reformulation research (2h)
- `1.2` – Table parsing behaviors & sparse cases (4h)
- `1.3` – Fixed-variable semantics analysis (first 2h)

### Prep Day 3
- `1.3` – Wrap fixed-variable findings (1h)
- `2.2` – max() reformulation design (3h)
- `2.3` – abs() handling options and decision matrix (3h)
- `1.4` – Nested $include handling: stack depth checks (1h)

### Prep Day 4
- `1.4` – Nested $include loop detection wrap-up (0.5h)
- `1.5` – Include path resolution & security guardrails (1.5h)
- `4.1` – GAMS emitter line-breaking strategy (3h)
- `6.1` – Confirm preprocessing pipeline leaves ModelIR unchanged; source map plan (3h)

**Sprint 4 can start once Prep Day 4 deliverables are signed off.**

### Sprint Day 1
- `3.1` – Evaluate scaling algorithms & select Curtis-Reid baseline (5h)
- `3.2` – Decide scaling application point via experiments (3h)

### Sprint Day 2
- `4.2` – Auxiliary variable naming (collision handling, indexing) (4h)
- `4.3` – Model declaration treatment for new constraints (3h)
- Buffer – Peer review / doc alignment (1h)

### Sprint Day 3
- `4.4` – MCP emission for fixed variables (4h)
- `6.2` – Fixed-variable KKT integration (4h)

### Sprint Day 4
- `6.4` – Auxiliary variables & IndexMapping alignment (4h)
- `6.3` – Scaling impact regression smoke tests (3h)
- Buffer – Documentation updates / contingency (1h)

### Sprint Day 5
- `5.1` – PATH behavior on nonlinear MCPs (full benchmarking block) (5h)
- `2.4` – PATH compatibility validation for non-smooth reformulations (3h)

### Sprint Day 6
- `5.3` – PATH failure reporting & listing parser (4h)
- `5.2` – Draft PATH option recommendations & CLI hooks (3h)
- Buffer – Hold for license-driven follow-ups (1h)

### Sprint Day 7 (Buffer)
- `5.4` – PATH initial point guidance experiments (2h)
- Reserved capacity for spillover, peer review, or additional PATH investigations (6h).

## Assumptions & Notes
- Schedule presumes 0.5h granularity; tasks split across days continue seamlessly.
- PATH-dependent activities (Tasks 2.4, 5.1, 5.2, 5.3, 5.4) are intentionally grouped at the end to wait for licensing. If access arrives earlier, these can be pulled forward.
- PATH solver is available locally. Example macOS path: `/Library/Frameworks/GAMS.framework/Versions/51/Resources/gams`.
  - For Windows, the PATH solver is typically installed at `C:\GAMS\gamsXX.X\gams.exe` (replace `XX.X` with your version).
  - For Linux, check your GAMS installation directory, e.g., `/opt/gams/gamsXX.X/gams` or as configured in your environment.
  - Please update the solver path in your environment as appropriate for your operating system.
- Day 7 intentionally left open to absorb overrun or handle newly discovered unknowns.
- Update `docs/planning/EPIC_1/SPRINT_4/KNOWN_UNKNOWNS.md` as items move from 🔍 to ✅ according to this cadence.
