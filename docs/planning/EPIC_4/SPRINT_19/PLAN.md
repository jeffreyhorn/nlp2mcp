# Sprint 19 Detailed Plan

**Created:** 2026-02-13
**Sprint Duration:** 14 days (Days 1-14)
**Estimated Effort:** 43-53 hours (~3-4h/day effective capacity)
**Risk Level:** MEDIUM-HIGH
**Day 0 Status:** COMPLETE (2026-02-13) — All 10 prep deliverables verified, 3,294 tests pass, SPRINT_LOG.md created
**Day 1 Status:** COMPLETE (2026-02-13) — Error taxonomy updated (24→0 internal_error), Subcategory G grammar fixes (+1 parse), 3,299 tests pass
**Day 2 Status:** COMPLETE (2026-02-16) — Put format specifiers (:width:decimals) + put_stmt_nosemi (6 models past parse), reserved word quoting in emit layer (ps2_f family inf/na quoted), 3,386 tests pass

---

## Executive Summary

Sprint 19 is the largest sprint in Epic 4, combining Sprint 18 deferred items with new lexer/grammar work and IndexOffset design. The prep phase (10 tasks) produced significant scope refinements:

- **lexer_invalid_char** baseline corrected from ~95 to 72 (target: below 30)
- **internal_error** count is 24, but 21/24 already parse with v1.2.0 (only 3 genuine failures remain)
- **IndexOffset IR** already exists — only AD integration remains (~8h, not 14-16h)
- **ISSUE_672** root cause identified as case sensitivity (2-4h, not 4-6h)
- **ISSUE_392/399** share root cause — combined fix (3-5h, not 4-8h separate)

These refinements reduce total expected effort and increase confidence in target achievability.

---

## Workstreams

### WS1: Sprint 18 Deferred Items (15-20h expected)

| Item | Effort | Priority | Prep Task |
|------|--------|----------|-----------|
| MCP infeasibility: circle (value capture) | 1.5-2h | High | Task 5 |
| MCP infeasibility: house (KKT formulation) | 2-4h | High | Task 5 |
| Subset relationship preservation | 1-2h | Medium | Task 5 (likely already done) |
| Reserved word quoting | 2-3h | High | Task 5 |
| Put statement format support | 2-2.5h | High | Task 5 |
| Lexer error quick wins (Phase 1) | 6-8h | High | Task 3 |

### WS2: FIX_ROADMAP Issues (15-23h)

| Item | Effort | Priority | Prep Task |
|------|--------|----------|-----------|
| ISSUE_670: Cross-indexed sums | 10-14h | P1 (Critical) | Task 4 |
| ISSUE_392/399: Table parsing | 3-5h | P2-P3 | Task 7 |
| ISSUE_672: MCP case sensitivity | 2-4h | P4 | Task 8 |

### WS3: lexer_invalid_char Grammar Fixes (14-18h)

| Phase | Models | Effort | Subcategories |
|-------|--------|--------|---------------|
| Phase 1: Quick wins | ~13 | 6-8h | G (set descriptions), C (put format), E (special values) |
| Phase 2: Core grammar | ~19+ | 10-13h | A (tuple/compound set), I (model/solve), B (cascading retest) |
| Phase 3: Advanced grammar | ~8+ | 8-10h | F (declaration gaps), D (lead/lag via IndexOffset) |

Note: Phase 1 quick wins are included in WS1 deferred items (lexer error quick wins). Phases 2-3 are the additional lexer work.

### WS4: internal_error Investigation (2-4h revised)

21/24 models already parse. Remaining work:
- Update error taxonomy with 5 new patterns (1h)
- Re-run pipeline to reclassify 21 silently-resolved models (0.5h)
- Fix gastrans (implicit index mapping) — medium effort (2h)
- Fix harker/mathopt4 (model attribute access) — overlaps with lexer Subcategory I (counted in WS3)

### WS5: IndexOffset AD Integration (8h)

- Extend `_apply_index_substitution()` in derivative_rules.py (4h)
- End-to-end pipeline tracing and validation (2h)
- Testing with 8 blocked models (2h)

---

## Revised Effort Summary

| Workstream | Original Estimate | Revised Estimate | Savings |
|------------|------------------|-----------------|---------|
| WS1: Deferred Items | 17-21h | 15-20h | 2h (subset likely done, lexer overlaps) |
| WS2: FIX_ROADMAP Issues | 16-28h | 15-23h | ISSUE_672 down from 4-6h to 2-4h |
| WS3: lexer_invalid_char | 14-18h | 10-15h | Phase 1 counted in WS1; phases 2-3 remain |
| WS4: internal_error | 6-8h | 2-4h | 21/24 already resolved |
| WS5: IndexOffset | 4h (design only) | 8h (full AD integration) | Expanded scope but design done |
| Pipeline Retest | 2h | 2h | — |
| **Total** | **43-53h** | **42-54h** | Net neutral (scope shifts) |

Note: Many items overlap across workstreams (e.g., put format is both WS1 and WS3 Phase 1; model attribute access is both WS3 and WS4). The day-by-day schedule below eliminates double-counting.

---

## 14-Day Schedule

### Week 1: Foundation + High-ROI Fixes (Days 1-7)

---

#### Day 1 — Setup + Quick Wins + Checkpoint 0
**Theme:** Sprint kickoff, verify baseline, start quick wins
**Effort:** 3-4h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Verify Sprint 19 branch setup, confirm all 3294 tests pass | 0.5h | Clean baseline confirmed |
| Re-run pipeline with updated error taxonomy (5 new patterns from Task 2) | 1h | Updated gamslib_status.json with 21 models reclassified |
| Implement set element description support (Subcategory G) | 1-2h | 4 models newly parsing |
| Run pipeline retest on affected models | 0.5h | Metrics updated |

**Checkpoint 0 Criteria:**
- All tests pass (3294+)
- Pipeline metrics match BASELINE_METRICS.md
- internal_error count drops from 24 to 3 (reclassification)
- 4 new models parsing (set element descriptions)

**Risks:** None — low-risk warm-up day
**Unknowns:** 6.2 (grammar ambiguities) — monitor during grammar changes

---

#### Day 2 — Put Statement Format + Reserved Word Quoting
**Theme:** Deferred items — well-scoped grammar + emit fixes
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Implement put statement `:width:decimals` format (Subcategory C) | 2-2.5h | Grammar updated, 6 models newly parsing |
| Implement reserved word quoting in expr_to_gams.py | 2-3h | ps2_f family models compile correctly |
| Run regression tests | 0.5h | Zero regressions confirmed |

**Risks:** Put grammar may interact with existing expression grammar
**Unknowns:** 5.1 (put format design — VERIFIED, design confirmed)

---

#### Day 3 — Special Values + Circle Model Fix ✅ COMPLETE
**Theme:** More quick wins + first MCP fix
**Effort:** 3-4h (actual: ~3h)

| Task | Effort | Deliverable |
|------|--------|-------------|
| Implement special values grammar subset (Subcategory E partial) | 2-3h | 4 models newly parsing (ship, tforss, ferts, lands) |
| Circle model MCP fix (execseed for deterministic evaluation) | 1-1.5h | circle MCP deterministic (infeasibility is KKT formulation issue, not randomness) |

**Risks:** Circle fix requires understanding of stochastic function handling
**Unknowns:** 1.1 (circle model — VERIFIED, approach confirmed)
**Outcome:** Grammar extended for special values in scalar data and indexed parameter data. Circle MCP now deterministic via execseed injection. 3413 tests, zero regressions.

---

#### Day 4 — ISSUE_672: MCP Case Sensitivity Fix
**Theme:** High-value solve fix — case normalization
**Effort:** 3-4h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Implement VarRef lowercase normalization in parser.py | 1h | VarRef nodes consistently lowercase |
| Unit tests for mixed-case differentiation | 0.5h | AD tests pass with normalized names |
| Regenerate alkyl/bearing MCP files | 0.5h | Correct stationarity equations |
| Run full regression suite | 0.5h | Zero regressions |
| Validate alkyl + bearing solve | 1h | Both models solve (or identify remaining issues) |

**Risks:** Emitted GAMS variables will be lowercase — verify readability acceptable
**Unknowns:** 8.4 (WRONG — case sensitivity, not bounds; fix designed in Task 8)

---

#### Day 5 — ISSUE_670: Cross-Indexed Sums (Part 1)
**Theme:** Start highest-ROI fix — analysis + implementation
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Implement `_collect_free_indices()` utility function | 3-4h | Function with unit tests |
| Begin integration into `_add_indexed_jacobian_terms()` | 1-2h | Initial integration |

**Risks:** Edge cases in free index collection with aliased indices
**Unknowns:** 8.1, 8.2 (VERIFIED — all 6 models share cross-indexed sum pattern)

---

#### Day 6 — ISSUE_670: Cross-Indexed Sums (Part 2) + Checkpoint 1
**Theme:** Complete ISSUE_670 + first major checkpoint
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Complete sum wrapping integration (indexed + scalar paths) | 2-3h | All stationarity paths handle free indices |
| Validate on abel (primary test model) | 1h | abel compiles and solves |
| Validate on remaining 5 models (qabel, chenery, mexss, orani, robert) | 1-2h | All 6 models compile |

**Checkpoint 1 Criteria (Day 6):**
- ≥13 new models parsing (from quick wins: G=4, C=6, E=3)
- internal_error reclassified (24 → 3 in pipeline)
- ISSUE_672 fixed (alkyl/bearing solve or advance)
- ISSUE_670 fix validated on abel (at minimum)
- circle model achieves model_optimal
- path_syntax_error reduced (6 → ≤2)
- Zero regressions in test suite
- Parse rate approaching 47%+ (75/159)

**Go/No-Go:** If ISSUE_670 fix is not working on abel by Day 6, descope to "investigation complete, defer fix to Day 7-8" and prioritize lexer grammar work.

---

#### Day 7 — ISSUE_670 Wrap-up + House Model Investigation
**Theme:** Complete ISSUE_670 edge cases + start house model
**Effort:** 3-4h

| Task | Effort | Deliverable |
|------|--------|-------------|
| ISSUE_670: Fix edge cases from Day 5-6 validation | 1-2h | All 6 models compile cleanly |
| House model MCP investigation (KKT formulation) | 2-3h | Root cause confirmed, fix designed or implemented |

**Risks:** House model may require deeper KKT analysis (up to 4h total)
**Unknowns:** 1.2 (house model — VERIFIED, complementarity contradiction identified)

---

### Week 2: Grammar Expansion + Integration (Days 8-14)

---

#### Day 8 — Tuple/Compound Set Data Grammar (Phase 2, Part 1)
**Theme:** Core grammar work — highest-impact lexer subcategory
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Implement dot-separated compound key syntax (Subcategory A) | 4-5h | Grammar parses tuple set data |
| Test on 2-3 representative models | 0.5h | Initial validation |

**Risks:** Grammar ambiguity with existing dot notation (HIGHEST RISK in sprint)
**Unknowns:** 6.1 (VERIFIED — syntax constructs cataloged), 6.2 (INCOMPLETE — monitor for ambiguities)

---

#### Day 9 — Tuple/Compound Set Data (Part 2) + Model/Solve Issues
**Theme:** Complete compound set + model attribute access
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Complete compound set data grammar, fix edge cases | 2-3h | 12 models newly parsing |
| Retest cascading models (Subcategory B) | 0.5h | ~10-12 cascading models resolve |
| Model/solve statement issues (Subcategory I) | 2-3h | 5 models newly parsing (overlaps with harker/mathopt4 from WS4) |

**Risks:** Cascading resolution may be lower than expected
**Unknowns:** 6.2 (INCOMPLETE — grammar ambiguity — active monitoring)

---

#### Day 10 — Table Parsing (ISSUE_392 + ISSUE_399) + Subset Verification
**Theme:** Deferred FIX_ROADMAP items
**Effort:** 3-4h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Table parsing semantic disambiguation (ISSUE_392 + ISSUE_399) | 3-4h | like model data correct; robert table parsed |
| Subset relationship verification (1h check) | 0.5-1h | Confirm subset declarations preserved or implement fix |

**Risks:** robert depends on both ISSUE_399 AND ISSUE_670 for full pipeline
**Unknowns:** 8.3 (VERIFIED — semantic fix, no grammar changes needed)

---

#### Day 11 — Declaration/Syntax Gaps + Checkpoint 2
**Theme:** Phase 3 grammar + major checkpoint
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Declaration/syntax gap fixes (Subcategory F) | 4-5h | 6 models newly parsing |
| Run full pipeline retest | 1h | Complete metrics snapshot |

**Checkpoint 2 Criteria (Day 11):**
- Parse rate ≥55% (≥87/159)
- lexer_invalid_char below 30 (target: fix 43+ models)
- internal_error below 15 (expected: 3 genuine + reclassified)
- All FIX_ROADMAP P1-P3 items complete (ISSUE_670, 392, 399)
- ISSUE_672 resolved
- circle + house solve status confirmed
- Test suite passes with zero regressions

**Go/No-Go:** If parse rate is below 50%, prioritize remaining lexer fixes over IndexOffset. If above 55%, proceed to IndexOffset as planned.

---

#### Day 12 — IndexOffset AD Integration (Part 1)
**Theme:** Enable lead/lag differentiation
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Extend `_apply_index_substitution()` for IndexOffset nodes | 4h | AD handles lead/lag variable references |
| Unit tests for IndexOffset differentiation | 1h | Tests confirm correct derivatives |

**Risks:** Index substitution logic may have unforeseen edge cases
**Unknowns:** 7.3 (VERIFIED — AD interaction design confirmed), 7.4 (VERIFIED — grammar already parses lead/lag)

---

#### Day 13 — IndexOffset Validation + Lead/Lag Grammar (Phase 3)
**Theme:** Complete IndexOffset + lead/lag subcategory
**Effort:** 4-5h

| Task | Effort | Deliverable |
|------|--------|-------------|
| End-to-end IndexOffset pipeline validation | 2h | Trace unsup_index_offset models through pipeline |
| Test 8 blocked models (launch, mine, sparta, tabora, ampl, otpop, robert, pak) | 2h | Models advance through pipeline |
| Lead/lag indexing grammar (Subcategory D) if not handled by IndexOffset | 1-2h | 4 models + 2 cascading |

**Risks:** Some blocked models may have additional issues beyond IndexOffset
**Unknowns:** None — all IndexOffset unknowns verified

---

#### Day 14 — Final Pipeline Retest + Documentation + Sprint Close
**Theme:** Validation, metrics, documentation
**Effort:** 3-4h

| Task | Effort | Deliverable |
|------|--------|-------------|
| Full pipeline retest (all 159 models) | 1h | Final gamslib_status.json |
| Compare final vs baseline metrics | 0.5h | Sprint 19 achievement summary |
| Update SPRINT_LOG.md with Day 14 metrics | 0.5h | Sprint log complete |
| Run full test suite, confirm zero regressions | 0.5h | Final test count recorded |
| Document any remaining issues for Sprint 20 | 0.5h | Carryover list |
| Tag release (v1.3.0 if targets met) | 0.5h | Release tagged |

**Final Acceptance Criteria:**
- lexer_invalid_char: below 30 (from 72)
- internal_error (parse): below 15 (from 24)
- Parse rate: ≥55% of valid corpus (from 38.4%)
- IndexOffset: AD integration complete, pipeline validates blocked models
- All tests pass; golden file tests for solving models unchanged
- circle and house achieve model_optimal (or documented blockers)
- put statement models parse

---

## Checkpoint Summary

| Checkpoint | Day | Key Criteria | Go/No-Go Decision |
|-----------|-----|-------------|-------------------|
| **CP0** | 1 | Baseline confirmed, 4 new parses, internal_error reclassified | Continue as planned |
| **CP1** | 6 | ≥13 new parses, ISSUE_670 on abel, ISSUE_672 fixed, circle solves | If ISSUE_670 not working: adjust Days 7-8 |
| **CP2** | 11 | Parse ≥55%, lexer <30, P1-P3 complete, zero regressions | If parse <50%: deprioritize IndexOffset |
| **Final** | 14 | All acceptance criteria met | Release v1.3.0 or document carryovers |

---

## Contingency Plans

### C1: ISSUE_670 takes longer than 14h
**Trigger:** Not working on abel by Day 6
**Response:** 
- Allocate Days 7-8 entirely to ISSUE_670 (defer house model to Day 10)
- If still blocked by Day 8, descope to "4/6 models fixed" (fix simplest cases, defer complex ones)
- **Descope candidate:** orani and robert (most complex cross-indexing patterns)

### C2: Grammar changes cause regressions
**Trigger:** Test failures after any grammar change
**Response:**
- Immediately revert the grammar change
- Run regression test to confirm revert restores green
- Redesign as semantic handler fix instead of grammar change
- **Prevention:** Run `make test` after every grammar change (never batch)

### C3: internal_error reclassification reveals deeper issues
**Trigger:** Re-running pipeline with new taxonomy shows unexpected failures
**Response:**
- Document new failure patterns
- Only fix patterns affecting 3+ models (high ROI)
- Defer single-model issues to Sprint 20
- **Budget:** 2h maximum for unexpected internal_error work

### C4: Compound set data grammar (Subcategory A) causes widespread ambiguities
**Trigger:** Grammar ambiguity errors or unexpected parse changes on existing models
**Response:**
- Fall back to semantic disambiguation (post-parse processing) instead of grammar changes
- Estimate +2-3h for semantic approach
- If semantic approach also fails, descope Subcategory A to Sprint 20
- **Impact:** Lose 12 models from parse count; may not reach ≥55% parse rate
- **Mitigation:** Phase 1 quick wins + ISSUE fixes should still push parse to ~50%

### C5: House model MCP fix requires deep investigation
**Trigger:** Root cause not clear after 3h on Day 7
**Response:**
- Cap house investigation at 4h total
- If not resolved, defer to Sprint 20 with documented findings
- Circle model fix is independent and should still complete
- **Impact:** 1 of 2 deferred MCP items deferred again — acceptable

### C6: IndexOffset AD integration is more complex than estimated
**Trigger:** Unit tests failing after 4h on Day 12
**Response:**
- Allocate Day 13 entirely to IndexOffset (defer lead/lag grammar)
- If still blocked, deliver "design documented + partial implementation" as deliverable
- IndexOffset IR design is already done — Sprint 20 can complete implementation
- **Impact:** 4-8 blocked models remain blocked; parse rate unaffected (they fail at translate, not parse)

---

## Scope Cut Priority (If Sprint Runs Over)

If total effort exceeds 53h, cut in this order (last item cut first):

| Priority | Item | Impact | Hours Saved |
|----------|------|--------|-------------|
| **MUST** | Quick wins (G, C, E) + ISSUE_670 + ISSUE_672 + internal_error reclass | Core targets | — |
| **MUST** | Compound set data grammar (A) + reserved words + put format | Parse rate target | — |
| **SHOULD** | Table parsing (ISSUE_392/399) | 2 models | 3-5h |
| **SHOULD** | House model MCP fix | 1 model solve | 2-4h |
| **COULD** | Declaration/syntax gaps (F) | 6 models | 4-5h |
| **COULD** | Lead/lag grammar (D) | 4 models | 3-4h |
| **DEFER** | Control flow (H), bracket/brace (J), misc (K) | 2-10 models | 8-12h |
| **DEFER** | IndexOffset AD integration (if parse target not met) | 4-8 translate models | 8h |

---

## Daily Metrics to Track

| Metric | Baseline | Day 6 Target | Day 11 Target | Day 14 Target |
|--------|----------|-------------|--------------|--------------|
| Parse success | 61/159 (38.4%) | 75/159 (47.2%) | 87/159 (54.7%) | ≥87/159 (≥55%) |
| lexer_invalid_char | 72 | ≤59 | ≤30 | <30 |
| internal_error (pipeline) | 24 | ≤5 | ≤3 | ≤3 |
| Translate success | 48 | 52+ | 55+ | 55+ |
| Solve success | 20 | 23+ | 25+ | 25+ |
| Full pipeline match | 7 | 9+ | 10+ | 10+ |
| path_syntax_error | 6 | ≤2 | ≤2 | ≤2 |
| Test count | 3,294 | 3,310+ | 3,340+ | 3,350+ |
| Regressions | 0 | 0 | 0 | 0 |

---

## Dependency Graph

```
Day 1: Error taxonomy update ─────────────────────────────────────────┐
Day 1: Set element descriptions (G) ──┐                              │
Day 2: Put format (C) ────────────────┤                              │
Day 2: Reserved word quoting ──────────┤                              │
Day 3: Special values (E) ────────────┤                              │
Day 3: Circle model fix ──────────────┤                              │
Day 4: ISSUE_672 (case sensitivity) ──┤                              │
                                      ├──▶ Day 6 Checkpoint 1       │
Day 5-6: ISSUE_670 (cross-indexed) ───┤                              │
Day 7: ISSUE_670 edge cases ──────────┘                              │
Day 7: House model ────────────────────────────────┐                  │
                                                   │                  │
Day 8-9: Compound set data (A) + Cascading (B) ───┤                  │
Day 9: Model/solve issues (I) ────────────────────┤                  │
Day 10: Table parsing (ISSUE_392/399) ────────────┤                  │
Day 10: Subset verification ──────────────────────┤                  │
Day 11: Declaration gaps (F) ─────────────────────┼──▶ Day 11 CP2   │
                                                   │                  │
Day 12-13: IndexOffset AD integration ────────────┤                  │
Day 13: Lead/lag grammar (D) ─────────────────────┤                  │
                                                   │                  │
Day 14: Full pipeline retest + release ────────────┴──────────────────┘
```

Key dependencies:
- **ISSUE_670** must complete before robert model fully validates (Day 10)
- **Compound set data grammar** (Days 8-9) must complete before cascading retest
- **IndexOffset AD** (Days 12-13) must complete before lead/lag grammar models validate
- **Error taxonomy update** (Day 1) should happen first to get accurate pipeline metrics throughout sprint

---

## Known Unknowns Integration

### Verified (22 of 26) — No Action Needed
All Critical and High unknowns are verified. Findings integrated into schedule above.

### Wrong (2 of 26) — Findings Incorporated
- **2.1** (Subset preservation): Already implemented in Sprint 17. Day 10 includes verification step.
- **8.4** (MCP pairing): Case sensitivity, not bounds. ISSUE_672 fix scheduled Day 4.

### Incomplete (2 of 26) — Scheduled for Monitoring
- **6.2** (Grammar ambiguities): Monitor during Days 8-9 compound set data work. Contingency C4 addresses this.
- **6.3** (Compile-time constants): Low priority. If encountered during grammar work, document for Sprint 20. Not a blocker for Sprint 19 targets.

---

## Success Criteria

Sprint 19 is successful if:
1. **lexer_invalid_char < 30** (from 72) — requires fixing 43+ models
2. **internal_error < 15** (from 24) — requires reclassification + 3 genuine fixes
3. **Parse rate ≥ 55%** (from 38.4%) — requires ≥87 parsing models (26+ new)
4. **IndexOffset AD integration complete** — 8 blocked models advance
5. **FIX_ROADMAP P1-P3 resolved** — ISSUE_670, 392, 399 fixed
6. **Zero regressions** — all existing tests pass, golden files unchanged
7. **circle and house solve** (or documented blockers)
8. **put statement models parse**
