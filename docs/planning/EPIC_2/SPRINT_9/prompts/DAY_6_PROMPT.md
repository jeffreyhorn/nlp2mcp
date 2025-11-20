# Day 6 Prompt: Equation Attributes → CHECKPOINT 3

**Branch:** Create a new branch named `sprint9-day6-equation-attributes-checkpoint3` from `sprint9-advanced-features`

**Objective:** Implement semantic handlers for equation attributes (.marginal, .l, .up, .lo), create IR representation for AttributeAccess nodes, validate with mingamma.gms, and achieve Checkpoint 3 (All parser features complete).

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 712-774) - Day 6 summary
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 8) - Equation attributes research
- Read `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (Unknowns 9.1.6, 9.1.7) - Attribute scope and semantics
- Verify Day 5 complete: Model sections working, hs62 parses, parse rate ≥60%
- Review mingamma.gms: `data/gamslib/mingamma.gms`
- **Key finding from Task 8:** Grammar already supports attributes, only semantic handlers needed

**Tasks to Complete (6-8 hours):**

1. **Implement semantic handler for equation attributes** (2-3 hours)
   - Open `src/ir/semantic_handler.py`
   - **Note:** Grammar already has attribute syntax (Task 8 discovery)
   - Implement handlers for attribute access:
     ```python
     def attribute_access(self, args):
         """Handle attribute access (e.g., eq.marginal, var.l)."""
         base = self.transform(args[0])  # Variable or equation reference
         attribute = str(args[1])  # Attribute name (.marginal, .l, .up, .lo)
         return AttributeAccess(base=base, attribute=attribute)
     ```
   - Support all 4 attribute types:
     - `.marginal` - Marginal value (dual/shadow price)
     - `.l` - Level value (primal value)
     - `.up` - Upper bound
     - `.lo` - Lower bound
   - Validate attribute exists for entity type (equations vs variables have different attributes)
   - Handle attribute access in expressions (RHS and LHS)

2. **Create IR AttributeAccess nodes** (1 hour)
   - Open `src/ir/nodes.py`
   - Add AttributeAccess node:
     ```python
     @dataclass
     class AttributeAccess(IRNode):
         """Represents attribute access on variable/equation (e.g., eq.marginal)."""
         base: IRNode  # VariableRef or EquationRef
         attribute: str  # "marginal", "l", "up", "lo"
         
         VALID_ATTRIBUTES = {"marginal", "l", "up", "lo", "m"}  # .m is alias for .marginal
         
         def __post_init__(self):
             """Validate AttributeAccess."""
             if self.attribute not in self.VALID_ATTRIBUTES:
                 raise ValueError(f"Invalid attribute: {self.attribute}")
             if not isinstance(self.base, IRNode):
                 raise TypeError(f"base must be IRNode, got {type(self.base)}")
     ```
   - Add IR traversal support
   - Add string representation

3. **Parse mingamma.gms (validate attributes)** (1 hour)
   - Run parser on mingamma.gms: `python -m src.parser data/gamslib/mingamma.gms`
   - Expected: Parse succeeds with attribute support
   - Verify AttributeAccess nodes created in IR
   - Check parse rate: Should be ≥60% (6-7/10 models)
   - Note: mingamma may have additional blockers beyond attributes

4. **Debug mingamma.gms failures (if any)** (0.5-1 hour)
   - If mingamma fails:
     - Check if failure is attribute-related or different blocker
     - Test minimal attribute example: "x = eq.marginal;"
     - Debug semantic handler
   - Test regression: Verify existing 6 models still parse

5. **Write attribute access tests** (1-1.5 hours)
   - Create or extend `tests/test_attributes.py`
   - Test cases:
     - `test_marginal_attribute()` - "eq.marginal" creates AttributeAccess
     - `test_level_attribute()` - "var.l" creates AttributeAccess
     - `test_upper_bound_attribute()` - "var.up" creates AttributeAccess
     - `test_lower_bound_attribute()` - "var.lo" creates AttributeAccess
     - `test_attribute_in_expression()` - "x = eq.marginal + 1;"
     - `test_attribute_assignment()` - "eq.marginal = value;"
     - `test_invalid_attribute()` - Should raise error
   - Integration test:
     ```python
     def test_mingamma_parses():
         """Verify mingamma.gms parses (if attributes are only blocker)."""
         result = parse_file("data/gamslib/mingamma.gms")
         # May still fail if other blockers exist
     ```
   - Target coverage: ≥80%

6. **Update dashboard with attribute statistics** (30 minutes)
   - Open `scripts/dashboard.py`
   - Add attribute metrics:
     ```python
     def count_attribute_usage(ir: ModelIR) -> dict:
         """Count attribute access usage."""
         return {
             "total_attributes": count_nodes(ir, AttributeAccess),
             "marginal_count": count_attribute_type(ir, "marginal"),
             "level_count": count_attribute_type(ir, "l"),
             "upper_bound_count": count_attribute_type(ir, "up"),
             "lower_bound_count": count_attribute_type(ir, "lo")
         }
     ```
   - Add column to dashboard for attribute usage
   - Regenerate dashboard

**Deliverables:**
- Updated `src/ir/semantic_handler.py` - Attribute semantic handler
- Updated `src/ir/nodes.py` - AttributeAccess node type
- mingamma.gms parsing status (success or documented blockers)
- Equation attribute test suite with ≥80% coverage
- Updated dashboard with attribute metrics

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Semantic handler creates AttributeAccess(variable="eq1", attribute="marginal")
  - [ ] IR correctly represents all 4 attribute types
  - [ ] mingamma.gms parsing attempted (document result)
  - [ ] Parse rate ≥60% (6-7/10 models)
  - [ ] All quality checks pass
  - [ ] **CHECKPOINT 3 PASSED** (see below)
- [ ] Mark Day 6 complete in PLAN.md
- [ ] Update README.md and CHANGELOG.md
- [ ] **Check off all Checkpoint 3 criteria in PLAN.md**

**Checkpoint 3 Criteria (PLAN.md lines 776-835):**
- [ ] Model sections fully implemented (Day 5)
- [ ] hs62.gms parses successfully
- [ ] Equation attributes fully implemented
- [ ] mingamma.gms parsing attempted (success or blockers documented)
- [ ] Parse rate ≥60% (6-7/10 models)
- [ ] All parser features tested with ≥80% coverage

**Checkpoint 3 Decision:**
- **GO:** All 6 criteria met → Proceed to Day 7 (conversion pipeline)
- **NO-GO:** Parser features incomplete → Spend Day 7 finishing parser, defer conversion to Day 8-9

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 9 Day 6: Equation Attributes → CHECKPOINT 3" \
             --body "Completes Day 6 tasks and achieves Checkpoint 3

## Equation Attributes Implementation
- Semantic handler for .marginal, .l, .up, .lo
- AttributeAccess IR nodes created
- All 4 attribute types supported

## mingamma.gms Status: [PASS/FAIL/PARTIAL]
- Parse result: [description]
- Parse rate: XX% (X/10 models)

## Checkpoint 3 Status: [PASS/NO-GO]
- [x] Model sections implemented
- [x] hs62 parses
- [x] Attributes implemented
- [x] mingamma attempted
- [x] Parse rate ≥60%
- [x] Test coverage ≥80%

## All Parser Features Complete ✅
Ready for Day 7 (conversion pipeline)." \
             --base sprint9-advanced-features
```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 712-835)
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 8)
- `data/gamslib/mingamma.gms`

**Notes:**
- Effort: 6-8h (2-3h semantic + 1h IR + 1h parse + 0.5-1h debug + 1-1.5h tests + 0.5h dashboard)
- Grammar already supports attributes (no grammar work needed)
- Checkpoint 3 is GO/NO-GO for conversion pipeline
- Parse rate target: ≥60% (may exceed if mingamma parses)
