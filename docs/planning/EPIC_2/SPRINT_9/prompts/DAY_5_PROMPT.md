# Day 5 Prompt: Model Sections

**Branch:** Create a new branch named `sprint9-day5-model-sections` from `sprint9-advanced-features`

**Objective:** Implement model section grammar production, semantic handlers for model declarations, create IR representation for ModelDeclaration nodes, and validate with hs62.gms.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 652-710) - Day 5 summary
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 4) - Model sections research
- Read `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (Unknowns 9.1.4, 9.1.5) - Model section syntax and grammar
- Verify Checkpoint 2 passed: i++1 working, himmel16 parses, parse rate ≥50%
- Review hs62.gms: `data/gamslib/hs62.gms`

**Tasks to Complete (5-6 hours):**

1. **Update GAMS grammar (model section production)** (1 hour)
   - Open `src/grammar/gams.lark`
   - Add model_statement production:
     ```lark
     model_statement: "Model" ID "/" model_members "/" ";"
     
     model_members: model_member ("," model_member)*
     
     ?model_member: ID                    -> model_member_id
                  | "all"                 -> model_member_all
     ```
   - Add to top-level statements:
     ```lark
     ?statement: variable_decl
               | parameter_decl
               | equation_decl
               | model_statement         // ADD THIS
               | assignment
               | ...
     ```
   - Test grammar:
     ```python
     parser.parse("Model m / eq1, eq2, var1 /;")
     parser.parse("Model mymodel / all /;")
     ```

2. **Implement semantic handler for model sections** (2-2.5 hours)
   - Open `src/ir/semantic_handler.py`
   - Implement model section handlers:
     ```python
     def model_statement(self, args):
         """Handle model section declaration."""
         name = str(args[0])  # Model name
         members = self.transform(args[1])  # model_members
         return ModelDeclaration(name=name, members=members)
     
     def model_members(self, args):
         """Handle model member list."""
         return [self.transform(arg) for arg in args]
     
     def model_member_id(self, args):
         """Handle named model member."""
         return ModelMember(type="reference", name=str(args[0]))
     
     def model_member_all(self, args):
         """Handle 'all' keyword in model."""
         return ModelMember(type="all", name=None)
     ```
   - Key semantic patterns from Task 4:
     - "Model name / eq1, eq2 /;" → References specific equations
     - "Model name / all /;" → References all equations
     - Multiple models per file supported
   - Validate model member references (equations/variables exist)

3. **Create IR ModelDeclaration nodes** (1 hour)
   - Open `src/ir/nodes.py`
   - Add ModelDeclaration and ModelMember nodes:
     ```python
     @dataclass
     class ModelMember(IRNode):
         """A member of a model (equation or variable reference)."""
         type: str  # "reference" or "all"
         name: Optional[str]  # Name if type="reference", None if type="all"
     
     @dataclass
     class ModelDeclaration(IRNode):
         """Represents a model section declaration."""
         name: str
         members: list[ModelMember]
         
         def __post_init__(self):
             """Validate ModelDeclaration."""
             if not isinstance(self.name, str):
                 raise TypeError(f"name must be str, got {type(self.name)}")
             if not isinstance(self.members, list):
                 raise TypeError(f"members must be list, got {type(self.members)}")
             for member in self.members:
                 if not isinstance(member, ModelMember):
                     raise TypeError(f"member must be ModelMember, got {type(member)}")
     ```
   - Add IR traversal support
   - Add string representation

4. **Parse hs62.gms (validate model sections)** (1 hour)
   - Run parser on hs62.gms: `python -m src.parser data/gamslib/hs62.gms`
   - Expected: Parse succeeds with model section support
   - Verify ModelDeclaration nodes created in IR
   - Check parse rate: Should increase to 60% (6/10 models)

5. **Debug hs62.gms failures (if any)** (0.5-1 hour)
   - If hs62 fails:
     - Check error message (model section related?)
     - Test minimal model section example
     - Debug semantic handler or IR construction
   - Test regression: Verify existing 5 models still parse

6. **Write model section tests** (1 hour)
   - Create or extend `tests/test_model_sections.py`
   - Test cases:
     - `test_model_with_named_members()` - "Model m / eq1, eq2 /;"
     - `test_model_with_all()` - "Model m / all /;"
     - `test_multiple_models()` - Multiple model declarations
     - `test_empty_model()` - "Model m / /;" (edge case)
     - `test_model_member_validation()` - Referenced equations exist
   - Integration test:
     ```python
     def test_hs62_parses():
         """Verify hs62.gms parses successfully."""
         result = parse_file("data/gamslib/hs62.gms")
         assert result.success
     ```
   - Target coverage: ≥80%

**Deliverables:**
- Updated `src/grammar/gams.lark` - Model section grammar
- Updated `src/ir/semantic_handler.py` - Model section handler
- Updated `src/ir/nodes.py` - ModelDeclaration and ModelMember nodes
- hs62.gms parsing successfully
- Model section test suite with ≥80% coverage

**Quality Checks:**
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Grammar parses "Model model_name / ..." syntax
- [ ] Semantic handler creates ModelDeclaration nodes
- [ ] IR correctly represents model structure
- [ ] hs62.gms parses successfully
- [ ] Parse rate ≥60% (5/10 → 6/10 with hs62)
- [ ] All quality checks pass
- [ ] Mark Day 5 complete in PLAN.md
- [ ] Update README.md and CHANGELOG.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 9 Day 5: Model Sections" \
             --body "Completes Day 5 tasks from Sprint 9 PLAN.md

## Model Sections Implementation
- Grammar supports 'Model name / members /;' syntax
- Semantic handler creates ModelDeclaration IR nodes
- Supports named members and 'all' keyword

## hs62.gms Status: [PASS/FAIL]
- Parse rate: XX% (X/10 models)

## Tests
- XX tests with ≥80% coverage
- All tests pass ✅

Ready for Day 6 (equation attributes)." \
             --base sprint9-advanced-features
```

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 652-710)
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 4)
- `data/gamslib/hs62.gms`

**Notes:**
- Effort: 5-6h total
- Model sections unlock hs62.gms (+10% parse rate)
- Straightforward implementation (single grammar production)
- No grammar conflicts expected
