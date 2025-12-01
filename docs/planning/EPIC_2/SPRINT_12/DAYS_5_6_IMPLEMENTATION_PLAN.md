# Sprint 12 Days 5-6: Implementation Plan

**Sprint:** Epic 2 - Sprint 12  
**Created:** 2025-12-01  
**Scope:** Days 5-6 (12h total, 2 days × 6h)  
**Status:** READY

---

## Executive Summary

### Day 4 Accomplishments

**Blockers Implemented (4-5h):**
1. ✅ **predefined_constants** (1h) - Unlocked fct.gms
2. ✅ **special_chars_in_identifiers** (1.5h) - Partially unlocked chenery.gms
3. ✅ **multiple_alias_declaration** (1.5h) - Partially unlocked jbearing.gms

**Models Unlocked:** 1/10 (10% parse rate)
- ✅ fct.gms - Fully parsing
- ⚠️ chenery.gms - Has additional blocker (table_wildcard_domain)
- ⚠️ jbearing.gms - Has additional blocker (curly_braces_sum)

**Remaining Time:** ~3h (within 8h time-box)

### Days 5-6 Scope

**Primary Goal:** Achieve 60-70% Tier 2 parse rate (6-7 models)

**Blockers to Implement:**
1. **inline_descriptions** (3h) - HIGH priority, unlocks 3 models
2. **model_inline_descriptions** (1.5h) - MEDIUM priority, unlocks 1 model
3. **Additional blockers** (variable, depends on discoveries)

**Stretch Goals:**
- table_wildcard_domain (5h) - LOW priority, but unlocks 3 models
- New blockers discovered during testing

---

## Phase 1: Blocker #4 - inline_descriptions (3-4h)

### Overview

**Priority:** HIGH (Score: 27)  
**Models Affected:** chem.gms, water.gms, gastrans.gms (3 models)  
**Complexity:** Medium (3h baseline + 1h buffer)  
**Expected Outcome:** 40% parse rate (4/10 models)

### Problem Statement

GAMS allows inline descriptions for set members:

```gams
Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
Set n 'nodes' / nw 'north west reservoir', 
                e 'east reservoir',
                ne 'north east reservoir' /;
```

Current parser rejects quoted strings after set member identifiers.

### Implementation Tasks

#### Task 1.1: Grammar Extension (1h)

**File:** `src/gams/gams_grammar.lark`

**Current Rule:**
```lark
?set_member: range_expr    -> set_range
           | ID            -> set_element
           | STRING        -> set_element
```

**Updated Rule:**
```lark
?set_member: range_expr                  -> set_range
           | ID STRING?                  -> set_element_with_desc
           | ID                          -> set_element
           | STRING                      -> set_element
```

**Multi-line Handling:**
- Grammar already handles multi-line via WS_INLINE/NEWLINE ignore
- No changes needed for continuation

**Test Cases:**
```gams
Set i / H 'hydrogen' /;                    # Single element with desc
Set j / a, b 'beta', c /;                  # Mixed: some with desc
Set k / x 'desc1', y 'desc2', z /;         # Multiple with desc
Set m / nw 'north west',                   # Multi-line
        se 'south east' /;
```

#### Task 1.2: AST Update (30min)

**File:** `src/ir/symbols.py`

**Current SetDef:**
```python
@dataclass
class SetDef:
    name: str
    members: list[str]  # Just member names
    domain: tuple[str, ...] = ()
    universe: Optional[str] = None
```

**Option A: Keep Simple (RECOMMENDED)**
Store only member names, discard descriptions:
```python
# No changes to SetDef - descriptions are parse-time only
```

**Option B: Store Descriptions**
```python
@dataclass
class SetElement:
    name: str
    description: Optional[str] = None

@dataclass
class SetDef:
    name: str
    members: list[str]  # Still just names for indexing
    member_details: dict[str, SetElement] = field(default_factory=dict)
    # ... rest unchanged
```

**Decision:** Use Option A - We don't need descriptions in IR for MCP generation

#### Task 1.3: Parser Updates (1h)

**File:** `src/ir/parser.py`

**Method:** `_extract_set_members()`

**Current Logic:**
```python
def _extract_set_members(self, node: Tree) -> list[str]:
    members = []
    for child in node.children:
        if child.data == "set_element":
            member_name = _token_text(child.children[0])
            members.append(member_name)
    return members
```

**Updated Logic:**
```python
def _extract_set_members(self, node: Tree) -> list[str]:
    members = []
    for child in node.children:
        if child.data == "set_element":
            # Legacy: ID only
            member_name = _token_text(child.children[0])
            members.append(member_name)
        elif child.data == "set_element_with_desc":
            # New: ID STRING? - take first token (ID)
            member_name = _token_text(child.children[0])
            # Ignore description (child.children[1] if present)
            members.append(member_name)
    return members
```

#### Task 1.4: Testing (1h)

**Unit Tests:** `tests/unit/test_inline_descriptions.py`

```python
def test_single_element_with_description():
    """Test set member with inline description."""
    source = """
    Set i 'atoms' / H 'hydrogen' /;
    """
    model = parse_model_text(source)
    assert "i" in model.sets
    assert "H" in model.sets["i"].members

def test_mixed_elements_some_with_descriptions():
    """Test set with mixed descriptions."""
    source = """
    Set i / a, b 'beta', c, d 'delta' /;
    """
    model = parse_model_text(source)
    assert model.sets["i"].members == ["a", "b", "c", "d"]

def test_multi_line_with_descriptions():
    """Test multi-line set with descriptions (gastrans pattern)."""
    source = """
    Set n 'nodes' / 
        nw 'north west reservoir',
        e 'east reservoir',
        ne 'north east reservoir',
        s 'south reservoir' /;
    """
    model = parse_model_text(source)
    assert len(model.sets["n"].members) == 4

def test_chem_exact_pattern():
    """Test exact pattern from chem.gms."""
    source = """
    Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
    """
    model = parse_model_text(source)
    assert model.sets["i"].members == ["H", "N", "O"]

def test_descriptions_with_special_chars():
    """Test descriptions containing special characters."""
    source = """
    Set i / a 'alpha (A)', b 'beta: B-value' /;
    """
    model = parse_model_text(source)
    assert len(model.sets["i"].members) == 2
```

**Integration Tests:** Parse full models
- `tests/fixtures/tier2_candidates/chem.gms`
- `tests/fixtures/tier2_candidates/water.gms`
- `tests/fixtures/tier2_candidates/gastrans.gms`

#### Task 1.5: Quality Checks (30min)

```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply fixes
make test       # Allow 9 known failures (golden files)
```

### Phase 1 Success Criteria

- ✅ Grammar accepts inline descriptions
- ✅ All unit tests pass (10+ tests)
- ✅ chem.gms parses successfully
- ✅ water.gms parses successfully
- ✅ gastrans.gms parses successfully
- ✅ Parse rate: 4/10 models (40%)
- ✅ No regressions (Tier 1 still passes)

---

## Phase 2: Blocker #5 - model_inline_descriptions (1.5-2h)

### Overview

**Priority:** MEDIUM (Score: 14)  
**Models Affected:** process.gms (1 model)  
**Complexity:** Simple (1.5h baseline + 0.5h buffer)  
**Expected Outcome:** 50% parse rate (5/10 models)

### Problem Statement

GAMS allows inline descriptions in Model statements:

```gams
Model transport 'shipment scheduling' / all /;
Model prodmix 'production mix' / resource, demand, profit /;
```

Current parser only supports:
```gams
Model transport / all /;
```

### Implementation Tasks

#### Task 2.1: Grammar Extension (30min)

**File:** `src/gams/gams_grammar.lark`

**Current Rules:**
```lark
model_stmt: ("Models"i | "Model"i) ID "/" "all"i "/" SEMI       -> model_all
          | ("Models"i | "Model"i) ID "/" model_ref_list "/" SEMI  -> model_with_list
```

**Updated Rules:**
```lark
model_stmt: ("Models"i | "Model"i) ID STRING? "/" "all"i "/" SEMI       -> model_all
          | ("Models"i | "Model"i) ID STRING? "/" model_ref_list "/" SEMI  -> model_with_list
```

**Note:** Similar pattern to inline_descriptions - add optional STRING after ID

#### Task 2.2: Parser Updates (30min)

**File:** `src/ir/parser.py`

**Method:** `_handle_model_stmt()`

Update to ignore STRING token if present:
```python
def _handle_model_stmt(self, node: Tree) -> None:
    if node.data == "model_all":
        # Extract model name (first ID token)
        model_name = _token_text(node.children[0])
        # Ignore description if present (STRING token)
        # ... rest of logic
```

#### Task 2.3: Testing (30min)

**Unit Tests:** `tests/unit/test_model_inline_descriptions.py`

```python
def test_model_all_with_description():
    source = """
    Model transport 'shipment scheduling' / all /;
    """
    model = parse_model_text(source)
    assert "transport" in model.models

def test_model_list_with_description():
    source = """
    Equation eq1, eq2;
    Model prodmix 'production model' / eq1, eq2 /;
    """
    model = parse_model_text(source)
    assert "prodmix" in model.models

def test_process_exact_pattern():
    """Test exact pattern from process.gms."""
    # Extract relevant lines from process.gms
    pass
```

### Phase 2 Success Criteria

- ✅ Model statements accept inline descriptions
- ✅ process.gms parses successfully
- ✅ Parse rate: 5/10 models (50%)

---

## Phase 3: Buffer & Stretch Goals (variable)

### Discovered Blockers

Based on Day 4 testing, additional blockers found:

1. **curly_braces_sum** (jbearing.gms, line 62)
   - Pattern: `sum{(nx,ny), expr}` instead of `sum((nx,ny), expr)`
   - Effort: 1-2h
   - Impact: Unlocks jbearing fully (if no other blockers)

2. **table_wildcard_domain** (chenery.gms, least.gms, like.gms)
   - Pattern: `Table pdat(lmh,*,sde,i)`
   - Effort: 5h (complex - wildcard domain handling)
   - Impact: Unlocks 3 models

### Decision Tree

**If ahead of schedule (>2h remaining):**
- Implement curly_braces_sum (quick win for jbearing)
- Start table_wildcard_domain (may carry to Day 7)

**If on schedule (≤2h remaining):**
- Document blockers for Day 7
- Focus on quality checks and PR

---

## Quality & Documentation (30min-1h)

### Quality Checklist

```bash
# Run before final commit
make typecheck
make lint
make format
make test

# Verify Tier 2 parse rate
python scripts/test_tier2_parsing.py
# Expected: 5-7 models (50-70%)

# Check golden file failures
pytest tests/e2e/test_golden.py -v
# Expected: 9 known failures (predefined constants)
```

### Documentation Updates

**Files to Update:**

1. **TIER_2_BLOCKER_ANALYSIS.md**
   - Mark blockers as implemented
   - Update parse rate statistics
   - Document any new blockers discovered

2. **Sprint 12 Retrospective**
   - Day 4 summary (models unlocked, time spent)
   - Days 5-6 summary (final parse rate)
   - Lessons learned
   - Blocker for Day 7 (if any)

3. **README or CHANGELOG** (if applicable)
   - Sprint 12 feature summary
   - Known limitations

---

## Timeline & Milestones

### Day 5 (6h)

**Morning (3h):**
- 09:00-10:00: Implement inline_descriptions grammar
- 10:00-11:00: Update parser for inline_descriptions
- 11:00-12:00: Unit tests for inline_descriptions

**Afternoon (3h):**
- 13:00-14:00: Integration tests (chem, water, gastrans)
- 14:00-15:00: Implement model_inline_descriptions
- 15:00-16:00: Test process.gms, quality checks

**Milestone:** 5/10 models parsing (50%)

### Day 6 (6h)

**Morning (3h):**
- 09:00-11:00: Implement curly_braces_sum (if time permits)
- 11:00-12:00: Test jbearing.gms fully

**Afternoon (3h):**
- 13:00-14:00: Start table_wildcard_domain OR document for Day 7
- 14:00-15:00: Final quality checks, golden file review
- 15:00-16:00: Documentation updates, PR creation

**Milestone:** 6-7/10 models parsing (60-70%)

---

## Risk Assessment

### High Risks

1. **inline_descriptions Multi-line Complexity**
   - **Risk:** gastrans.gms may have complex continuation logic
   - **Mitigation:** Test gastrans early, adjust grammar if needed
   - **Contingency:** Skip gastrans, focus on chem/water (still 50% rate)

2. **New Blockers in Models**
   - **Risk:** chem/water/process may have additional blockers
   - **Mitigation:** Test models incrementally after each blocker fix
   - **Contingency:** Document new blockers for Day 7, focus on known wins

### Medium Risks

1. **Time Overrun on inline_descriptions**
   - **Risk:** Takes 4h instead of 3h
   - **Mitigation:** Use buffer time (1h allocated)
   - **Contingency:** Defer model_inline_descriptions to Day 6

2. **Golden File Test Failures**
   - **Risk:** Predefined constants change expected output
   - **Mitigation:** Already documented as known issue
   - **Contingency:** Update golden files at end of Sprint 12

---

## Success Metrics

### Minimum Success (Days 5-6)

- ✅ inline_descriptions implemented and tested
- ✅ 4/10 models parsing (40%)
- ✅ No regressions in Tier 1 tests
- ✅ PR ready for review

### Target Success

- ✅ inline_descriptions + model_inline_descriptions implemented
- ✅ 5/10 models parsing (50%)
- ✅ Documentation complete

### Stretch Success

- ✅ All above + curly_braces_sum
- ✅ 6/10 models parsing (60%)
- ✅ table_wildcard_domain started (even if incomplete)

---

## Appendix: Blocker Status Matrix

| Blocker | Status | Effort | Models | Parse Rate Impact |
|---------|--------|--------|--------|-------------------|
| predefined_constants | ✅ Done (Day 4) | 1h | fct | +10% (1/10) |
| special_chars_in_identifiers | ✅ Done (Day 4) | 1.5h | chenery* | +0% (blocked) |
| multiple_alias_declaration | ✅ Done (Day 4) | 1.5h | jbearing* | +0% (blocked) |
| inline_descriptions | 🔄 Day 5 | 3-4h | chem, water, gastrans | +30% (4/10) |
| model_inline_descriptions | 📋 Day 5-6 | 1.5h | process | +10% (5/10) |
| curly_braces_sum | 📋 Stretch | 1-2h | jbearing | +10% (6/10) |
| table_wildcard_domain | 📋 Day 7+ | 5h | chenery, least, like | +30% (9/10) |

*Partially unlocked - has additional blockers

---

**Plan Status:** READY  
**Next Action:** Begin Day 5 - Phase 1: inline_descriptions
