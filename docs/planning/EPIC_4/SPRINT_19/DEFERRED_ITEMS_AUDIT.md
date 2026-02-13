# Sprint 18 Deferred Items Readiness Audit

**Created:** February 13, 2026
**Status:** Complete
**Purpose:** Verify all 5 Sprint 18 deferred items have sufficient context, code pointers, and test plans for efficient Sprint 19 implementation

---

## Executive Summary

All 5 Sprint 18 deferred items have been audited. Key findings:

1. **MCP Infeasibility Bug Fixes (3-4h):** Two distinct root causes confirmed. Circle requires parameter value capture for `uniform()`. House has a deeper constraint qualification / KKT formulation issue. Effort estimate may need upward revision for house.
2. **Subset Relationship Preservation (4-5h):** IR metadata and emission code already implemented (Sprint 17 Day 5). The ~3 affected models are **not identified** in documentation. May already be resolved — needs model-level verification during Sprint 19. Effort estimate may decrease to 1-2h if issue is already fixed.
3. **Reserved Word Quoting (2-3h):** Fix is well-scoped. Affects models using GAMS reserved constants (`inf`, `na`, `eps`) as set element indices. Implementation location confirmed: `src/emit/expr_to_gams.py`. Sprint 18 P1 quoting fix partially addresses the problem (multi-char element quoting), but reserved constants need explicit handling. Effort estimate confirmed.
4. **Lexer Error Deep Analysis (5-6h):** Prep Task 3 (not yet completed) will produce the subcategorization catalog. The deferred item's scope significantly overlaps with Prep Task 3. Recommend: treat Prep Task 3 output as satisfying the analysis deliverable; reallocate remaining budget (2-3h) to initial quick-win grammar fixes.
5. **Put Statement Format Support (2.5h):** Well-researched in Sprint 18. Grammar extension location confirmed. 3 of 4 models blocked by `:width:decimals` only; stdcge needs an additional `put_stmt_nosemi` fix. No secondary issues found for the 3 format-specifier models. Effort estimate confirmed at 2-2.5h.

**Overall Readiness:** HIGH — All items have sufficient context for implementation. Two items (subset preservation, lexer analysis) may have reduced scope. No blockers identified.

---

## Item 1: MCP Infeasibility Bug Fixes (3-4h)

### Affected Models

| Model | Error Category | Current Status | Root Cause |
|-------|---------------|----------------|------------|
| circle | model_infeasible | PATH solver fails | `uniform()` regenerates different random data in MCP context |
| house | model_infeasible | PATH solver fails | Constraint qualification failure / KKT formulation issue |

### Circle Model Analysis

**Source:** `data/gamslib/raw/circle.gms`
**Generated MCP:** `data/gamslib/mcp/circle_mcp.gms`

**Root Cause:** The circle model uses `uniform(1,10)` to generate random data for parameters `x(i)` and `y(i)`. The MCP emission preserves the `uniform()` function call rather than the computed values. When GAMS executes the MCP file, new random values are generated, making the KKT conditions inconsistent with the original NLP solution.

**Evidence from generated MCP:**
```gams
x(i) = uniform(1, 10);   % Regenerates different values each run
y(i) = uniform(1, 10);
```

**Fix Approach:** Capture computed parameter values from the original NLP execution and emit them as constants in the MCP file:
```gams
x("p1") = 5.091;  x("p2") = 17.179;  ...   % Hardcoded original values
y("p1") = 19.966;  y("p2") = 2.345;   ...
```

**Fix Location:** `src/emit/original_symbols.py` — modify parameter emission to detect function-call expressions (`uniform`, `normal`, etc.) and substitute captured values. Alternative: `src/ir/parser.py` — capture evaluated values during parsing.

**Verification:** Check if `execseed` (GAMS random seed) is a simpler alternative to value capture. If fixing the seed makes the MCP solvable, the fix is simpler.

**Sprint 18 Code Changes Impact:** The P5 variable initialization fix (`src/emit/emit_gams.py:94-171`) does not affect this issue — the problem is in parameter data, not variable initialization.

### House Model Analysis

**Source:** `data/gamslib/raw/house.gms`
**Generated MCP:** `data/gamslib/mcp/house_mcp.gms`

**Root Cause:** The house model's MCP formulation produces infeasible complementarity constraints. Analysis of the generated MCP listing shows:
- Contradictory complementarity conditions (e.g., `comp_maxw` requires `-x >= 0` while `comp_minw` requires `x >= 0`)
- Multiple variables uninitialized (y, z, a, a1, a2, ta default to 0)
- Bound complementarity equations show initial infeasibility

**Fix Approach:** Requires deeper investigation:
1. Extract KKT point from original NLP solution (the original solves successfully with CONOPT, obj=4500)
2. Verify if the KKT point satisfies the generated MCP system
3. If not, identify formulation gap in KKT assembly (`src/kkt/assemble.py`) or stationarity generation (`src/kkt/stationarity.py`)

**Fix Location:** Likely `src/kkt/assemble.py` for complementarity pairing and/or `src/kkt/stationarity.py` for stationarity equation construction.

**Risk:** House may require more investigation than the 3-4h budget allows. The constraint qualification analysis alone could take 2-3h.

### Effort Estimate Assessment

| Sub-item | Original | Revised | Notes |
|----------|----------|---------|-------|
| Circle fix | ~1.5h | 1.5-2h | Parameter value capture is well-scoped |
| House fix | ~1.5h | 2-4h | May require KKT formulation investigation |
| **Total** | **3-4h** | **3.5-6h** | House risk drives upper bound |

### Regression Risk

**Low.** Both fixes are model-specific:
- Circle: Only models with `uniform()` or stochastic parameter expressions are affected
- House: Fix will target specific constraint/bound configurations

The 20 currently-solving models do not use `uniform()` and have working MCP formulations.

### Code Pointers

| Component | File | Key Functions/Lines |
|-----------|------|-------------------|
| Parameter emission | `src/emit/original_symbols.py` | `emit_original_parameters()`, `emit_computed_parameter_assignments()` |
| Variable init (P5) | `src/emit/emit_gams.py` | Lines 94-171 (already implemented, not the fix target) |
| KKT assembly | `src/kkt/assemble.py` | `assemble_kkt_system()` |
| Stationarity | `src/kkt/stationarity.py` | `build_stationarity_equations()` |
| Complementarity | `src/kkt/partition.py` | Complementarity pair generation |

---

## Item 2: Subset Relationship Preservation (4-5h)

### Affected Models

**Status: UNCONFIRMED.** The PROJECT_PLAN.md states "~3 models affected" but no specific models are identified in any documentation.

Sprint 18 Day 1 analysis identified 2 models (abel, qabel) with GAMS Error 352 ("Set not initialized"), but this was resolved by the P4 fix (Dynamic Subset Assignment), which is a **different issue** from subset relationship declarations.

### IR Metadata Status

**VERIFIED: Metadata is properly stored.**

`SetDef.domain` in `src/ir/symbols.py:31-36` stores parent set information:
```python
@dataclass
class SetDef:
    name: str
    members: list[str] = field(default_factory=list)
    domain: tuple[str, ...] = ()  # Parent set(s) for subsets
```

Example: subset `cg` of `genchar` stored as `SetDef(name='cg', domain=('genchar',))`.

### Emission Code Status

**VERIFIED: Subset emission is already implemented.**

`_format_set_declaration()` in `src/emit/original_symbols.py:188-237` correctly handles subset declarations:
- Checks `set_def.domain` to determine if set is a subset
- Formats domain as parenthesized list (e.g., `cg(genchar) /a, b, c/`)
- Multi-dimensional subsets supported (e.g., `arc(n,np)`)
- Domain parent names properly quoted via `_quote_symbol()`

`emit_original_sets()` in `src/emit/original_symbols.py:384-450` calls this function and includes a Sprint 17 Day 5 comment: "Now preserves subset relationships by emitting domain."

### Unit Test Coverage

Tests exist in `tests/unit/emit/test_original_symbols.py`:
- `test_subset_with_domain()` (lines 57-70): Verifies `cg(genchar) /a, b, c/` output
- `test_subset_without_members()` (lines 72-86): Verifies `sub(parent)` output
- `test_multi_dimensional_subset()` (lines 88-101): Verifies `arc(n,np)` output

### Sprint 18 Code Changes Impact

Sprint 18 made several set-related changes, none of which break subset preservation:
- **Issue #666** (commit 2eb784f): Fixed KKT domain mismatch with subset variables — different code path
- **Issue #664** (commit a7b1f06): Element quoting — compatible with subset domain quoting
- **P4 fix**: Dynamic subset assignment — complementary feature, not conflicting

### Assessment

The subset relationship preservation feature appears to be **already implemented** from Sprint 17. The "~3 affected models" may refer to:
1. Models that were fixed by P4 (dynamic subsets — abel, qabel) — already resolved
2. Models where the parser doesn't capture subset relationships — needs investigation
3. Models where the IR has domain info but it's incomplete — needs investigation

**Recommendation:** During Sprint 19, run a quick verification (1h):
1. Identify all models where the original GAMS uses `Set i(j)` syntax
2. Generate MCP output and check if subset declarations are preserved
3. If all subset declarations are correct, mark this item as already complete

### Effort Estimate Assessment

| Scenario | Effort | Probability |
|----------|--------|------------|
| Already fixed (verification only) | 1-2h | 60% |
| Parser doesn't capture some subset relationships | 4-5h | 30% |
| Emission code has edge case bugs | 2-3h | 10% |

### Code Pointers

| Component | File | Key Functions/Lines |
|-----------|------|-------------------|
| SetDef with domain | `src/ir/symbols.py` | Lines 31-36 |
| Set declaration formatting | `src/emit/original_symbols.py` | `_format_set_declaration()` lines 188-237 |
| Set emission | `src/emit/original_symbols.py` | `emit_original_sets()` lines 384-450 |
| Unit tests | `tests/unit/emit/test_original_symbols.py` | Lines 57-101 |

---

## Item 3: Reserved Word Quoting (2-3h)

### Affected Models

Models that use GAMS reserved constants or keywords as identifiers:

| Model | Reserved Words Used | GAMS Error Codes |
|-------|-------------------|-----------------|
| ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s | `inf`, `eff` as set element indices | 120, 145, 149, 340 |

**Note:** `pollut` was previously listed as affected but was fixed by Sprint 18 P1 (element literal quoting). The remaining issue is specifically about GAMS reserved constants (`inf`, `na`, `eps`, `undf`) and potentially reserved keywords used as identifiers.

### Current Quoting Implementation

`_quote_indices()` in `src/emit/expr_to_gams.py:144-212` applies heuristic-based quoting:
- Single lowercase letters (i, j, k) → NOT quoted (domain variables)
- Two-letter lowercase → NOT quoted
- Multi-letter lowercase → QUOTED as element literals (Sprint 18 P1 fix)
- Contains digits or uppercase → QUOTED

**What's Missing:**
- No GAMS reserved constant detection (`inf`, `na`, `eps`, `undf`, `yes`, `no`)
- No GAMS reserved keyword detection for identifiers
- No `GAMS_RESERVED_WORDS` constant anywhere in codebase

### Sprint 18 Quoting Fixes

- **P1 (Day 2):** Element literal quoting — handles multi-char lowercase names but **not** reserved words specifically
- **P2 (Day 3):** Lag/lead quoting — handles IndexOffset objects, unrelated to reserved words
- **Neither fix** addresses the reserved constant issue: `inf` is 3 letters, lowercase, so the heuristic may or may not quote it depending on context

### Proposed Fix

1. Add `GAMS_RESERVED_CONSTANTS` set to `src/emit/expr_to_gams.py`:
   ```python
   GAMS_RESERVED_CONSTANTS = {'inf', 'na', 'eps', 'undf', 'yes', 'no'}
   ```

2. Modify `_quote_indices()` to check against reserved constants before applying heuristics

3. Check all other emission points for reserved word handling:
   - `src/emit/original_symbols.py` — set element emission
   - `src/emit/model.py` — model declaration
   - `src/emit/equations.py` — equation definitions (delegates to `expr_to_gams()`)

### GAMS Reserved Words List

From `src/gams/gams_grammar.lark` keyword tokens and GAMS documentation:

**Constants:** `inf`, `-inf`, `na`, `eps`, `undf`, `yes`, `no`

**Keywords (potentially used as identifiers):** `set`, `parameter`, `variable`, `equation`, `model`, `solve`, `option`, `display`, `put`, `file`, `loop`, `if`, `else`, `while`, `for`, `repeat`, `until`, `abort`, `scalar`, `table`, `alias`

**Built-in functions:** `abs`, `exp`, `log`, `sqrt`, `sin`, `cos`, `min`, `max`, `ord`, `card`, `uniform`, `normal`, `round`, `mod`, `ceil`, `floor`, `power`, `sqr`

### Effort Estimate Assessment

| Task | Effort |
|------|--------|
| Create reserved words constant + modify `_quote_indices()` | 1h |
| Check other emission points | 0.5h |
| Test on affected models | 0.5-1h |
| **Total** | **2-2.5h** |

**Estimate confirmed** at 2-3h. No upward revision needed.

### Code Pointers

| Component | File | Key Functions/Lines |
|-----------|------|-------------------|
| Index quoting | `src/emit/expr_to_gams.py` | `_quote_indices()` lines 144-212 |
| Mixed index formatting | `src/emit/expr_to_gams.py` | `_format_mixed_indices()` lines 113-142 |
| Expression converter | `src/emit/expr_to_gams.py` | `expr_to_gams()` lines 261-450 |
| Set element emission | `src/emit/original_symbols.py` | `_sanitize_set_element()`, `_quote_symbol()` |
| Grammar keywords | `src/gams/gams_grammar.lark` | FUNCNAME terminal (~line 1535), keyword terminals |

---

## Item 4: Lexer Error Deep Analysis (5-6h)

### Overlap with Prep Task 3

Prep Task 3 (Catalog lexer_invalid_char Subcategories) is currently **NOT STARTED** (per PREP_PLAN.md). When completed, it will produce `LEXER_ERROR_CATALOG.md` containing:
- Full subcategorization of all lexer_invalid_char failures
- Model count per subcategory
- Grammar-change feasibility assessment per subcategory
- Implementation order recommendation

The deferred "Lexer Error Deep Analysis" item from PROJECT_PLAN.md specifies:
- Full subcategorization of remaining parse failures
- Run all parse-stage failure models with verbose output
- Group by error type and create subcategory clusters
- Deliverable: `LEXER_ERROR_ANALYSIS.md` with error categories and fix priorities

### Scope Comparison

| Aspect | Prep Task 3 | Deferred Item 4 |
|--------|-------------|-----------------|
| Subcategorize failures | Yes | Yes |
| Identify blockers by count | Yes | Yes |
| Estimate implementation time | Yes | Yes |
| Grammar-only vs preprocessor | Yes | No (not specified) |
| Initial fix implementation | No | Not specified but implied |
| Deliverable name | `LEXER_ERROR_CATALOG.md` | `LEXER_ERROR_ANALYSIS.md` |

### Recommendation

Prep Task 3 output **substantially satisfies** the deferred item's deliverable. The key difference:
- Prep Task 3 = analysis and catalog (research)
- Deferred item = analysis + potentially initial fixes (implementation)

**Proposed scope boundary:**
1. Treat Prep Task 3 output as the analysis deliverable (rename or merge into `LEXER_ERROR_ANALYSIS.md`)
2. Reallocate 3-4h of the deferred item's 5-6h budget to initial quick-win grammar fixes identified by the catalog
3. Keep 1-2h for any additional analysis beyond the catalog (e.g., preprocessor interaction patterns)

### Sprint 18 Prior Analysis

Sprint 18 Day 1 parse error breakdown documented:
- `lexer_invalid_char`: 72 models (at baseline)
- `internal_error`: 24 models
- `semantic_undefined_symbol`: 2 models

No detailed subcategorization was performed during Sprint 18 (deferred to Sprint 19).

### Effort Estimate Assessment

| Scenario | Effort |
|----------|--------|
| Prep Task 3 fully satisfies analysis | 0h additional (5-6h saved) |
| Prep Task 3 + gap analysis | 1-2h additional |
| Prep Task 3 + initial grammar fixes | 3-4h additional |
| **Recommended** | **Reallocate to grammar fixes** |

### Code Pointers

| Component | File | Key Locations |
|-----------|------|--------------|
| Grammar | `src/gams/gams_grammar.lark` | All rules (~1600 lines) |
| Parser | `src/ir/parser.py` | Semantic handlers |
| Prep Task 3 spec | `docs/planning/EPIC_4/SPRINT_19/PREP_PLAN.md` | Lines 315-408 |

---

## Item 5: Put Statement Format Support (2.5h)

### Sprint 18 Research Review

`docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md` provides thorough analysis:
- Verified format specifier syntax: `:width` and `:width:decimals` (no three-part variant)
- Optional alignment prefix: `:<`, `:>`, `:<>` before width
- Scientific notation controlled by global `.nr` setting, not per-item specifiers
- Sprint 18 Unknown 3.1 verified: `:width:decimals` is the primary format
- Sprint 18 Unknown 3.2 verified: 3 of 4 models blocked only by `:width:decimals`; stdcge needs separate fix
- Sprint 18 Unknown 3.3 verified: No conflict with existing colon usage in grammar

### Target Model Status

| Model | Blocking Issue | Secondary Issues | Will Parse After Fix? |
|-------|---------------|-----------------|----------------------|
| ps5_s_mn | `:width:decimals` not supported | None | Yes |
| ps10_s | `:width:decimals` not supported | None | Yes |
| ps10_s_mn | `:width:decimals` not supported | None | Yes |
| stdcge | `put_stmt_nosemi` missing | Not `:width:decimals` | No (needs separate fix) |

**Confirmed:** 3 models blocked by `:width:decimals` only. stdcge's actual issue is `loop(j, put j.tl);` without proper semicolon handling in loop context — requires a `put_stmt_nosemi` grammar variant.

### Grammar Extension Location

**File:** `src/gams/gams_grammar.lark` (lines 493-500)

**Current grammar:**
```lark
put_stmt: "put"i put_items? SEMI
        | "put"i put_items "/" SEMI

put_items: put_item (","? put_item)*

put_item: STRING
        | "/" -> put_newline
        | expr
```

**Proposed extension:**
```lark
put_item: STRING put_format?
        | "/" -> put_newline
        | expr put_format?

put_format: ":" PUT_ALIGN? NUMBER (":" NUMBER)?
PUT_ALIGN: "<>" | "<" | ">"
```

**Conflict check:** No conflicts — colon is not used in any grammar rule that could be active within a `put_item` expression context.

### Sprint 18 Code Changes Impact

Sprint 18 did not modify put statement grammar rules. The existing `put_stmt` rule is unchanged from pre-Sprint 18.

### Effort Estimate Assessment

| Task | Effort |
|------|--------|
| Add `put_format` rule to grammar | 0.5h |
| Add `put_stmt_nosemi` variant | 0.5h |
| Parser semantic handler (if needed) | 0.5h |
| Test on all 4 models | 0.5h |
| Unit tests | 0.5h |
| **Total** | **2-2.5h** |

**Estimate confirmed** at 2.5h. No revision needed.

### Code Pointers

| Component | File | Key Locations |
|-----------|------|--------------|
| Put grammar rules | `src/gams/gams_grammar.lark` | Lines 493-500 |
| Put format analysis | `docs/planning/EPIC_4/SPRINT_18/PUT_FORMAT_ANALYSIS.md` | Full document |
| Target models | `data/gamslib/raw/` | ps5_s_mn.gms, ps10_s.gms, ps10_s_mn.gms, stdcge.gms |

---

## Summary: Readiness Assessment

| Item | Ready? | Blockers | Effort Revision | Key Risk |
|------|--------|----------|----------------|----------|
| 1. MCP Infeasibility | Yes | None | 3-4h → 3.5-6h (house risk) | House may need deeper KKT investigation |
| 2. Subset Preservation | Yes | Need to identify affected models | 4-5h → 1-5h (may be done) | Possibly already implemented |
| 3. Reserved Word Quoting | Yes | None | 2-3h confirmed | Low risk |
| 4. Lexer Error Analysis | Yes* | Depends on Prep Task 3 | 5-6h → reallocate to fixes | Scope overlap with Prep Task 3 |
| 5. Put Format Support | Yes | None | 2.5h confirmed | Low risk |

*Item 4 readiness depends on Prep Task 3 completion providing the catalog.

### Prerequisites Check

- [x] No missing prerequisites identified
- [x] All code pointers verified against current codebase
- [x] Sprint 18 code changes checked for impact on each item
- [x] Overlap between Lexer Error Deep Analysis and Prep Task 3 clarified
- [x] Effort estimates confirmed or updated with rationale

### Total Effort

| Scenario | Effort Range |
|----------|-------------|
| **Optimistic** (subset done, lexer → fixes) | 12-16h |
| **Expected** | 15-20h |
| **Pessimistic** (house deep dive, subset not done) | 20-25h |
| **Original estimate** | 17-21h |
