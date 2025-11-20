# Day 3 Prompt: Advanced Indexing - Part 1

**Branch:** Create a new branch named `sprint9-day3-i-plusplus-1-part1` from `sprint9-advanced-features`

**Objective:** Implement i++1, i--1 grammar changes, implement semantic handlers for arithmetic indexing, and create IR representation for IndexExpression nodes.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 340-463) - Day 3 detailed plan with implementation details
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 3) - i++1 indexing research and design
- Read `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (Unknowns 9.1.1, 9.1.2, 9.1.3) - i++1 complexity, grammar, semantics
- Verify Checkpoint 1 passed: Test infrastructure complete, fast tests <30s
- Review grammar design from Task 3 (token-level disambiguation approach)

**Tasks to Complete (4-5 hours):**

1. **Update GAMS grammar (i++1, i--1 patterns)** (1-1.5 hours)
   - Open `src/grammar/gams.lark`
   - Add tokens for circular lead/lag operators:
     ```lark
     CIRCULAR_LEAD: "++"
     CIRCULAR_LAG: "--"
     ```
   - Update `index_expression` production to support arithmetic indexing:
     ```lark
     ?index_expr: ID                              -> indexed_plain
                | ID lag_lead_suffix             -> indexed_with_offset
     
     lag_lead_suffix: CIRCULAR_LEAD offset_expr   -> circular_lead
                    | CIRCULAR_LAG offset_expr    -> circular_lag
                    | PLUS offset_expr            -> linear_lead
                    | MINUS offset_expr           -> linear_lag
     
     offset_expr: NUMBER                          -> offset_number
                | ID                              -> offset_variable
     ```
   - Key design decisions from Task 3:
     - Token-level: `++` matches before `+` (longest match wins)
     - Context separation: Indexing context vs arithmetic context use different rules
     - No grammar conflicts with existing arithmetic operators
   - Test grammar changes immediately:
     ```python
     # Test synthetic examples (don't wait for Day 4)
     parser.parse("x(i)")      # Should work (baseline)
     parser.parse("x(i++1)")   # Should work (circular lead)
     parser.parse("x(i--2)")   # Should work (circular lag)
     parser.parse("x(i+j)")    # Should work (linear lead with variable)
     ```

2. **Implement semantic handler for arithmetic indexing** (2-2.5 hours)
   - Open `src/ir/semantic_handler.py`
   - Implement handlers for new grammar rules:
     ```python
     def indexed_with_offset(self, args):
         """Handle indexed reference with lead/lag offset."""
         base = args[0]  # ID token
         offset_tree = args[1]  # lag_lead_suffix tree
         return self.transform(offset_tree, base=base)
     
     def circular_lead(self, args, base):
         """Handle circular lead (++) operator."""
         offset = self.transform(args[0])  # offset_expr
         return IndexOffset(base=str(base), offset=offset, circular=True)
     
     def circular_lag(self, args, base):
         """Handle circular lag (--) operator."""
         offset = self.transform(args[0])  # offset_expr
         # Negate offset for lag
         negated = BinaryOp(op="-", left=Const(0), right=offset)
         return IndexOffset(base=str(base), offset=negated, circular=True)
     
     def linear_lead(self, args, base):
         """Handle linear lead (+) operator."""
         offset = self.transform(args[0])
         return IndexOffset(base=str(base), offset=offset, circular=False)
     
     def linear_lag(self, args, base):
         """Handle linear lag (-) operator."""
         offset = self.transform(args[0])
         negated = BinaryOp(op="-", left=Const(0), right=offset)
         return IndexOffset(base=str(base), offset=negated, circular=False)
     
     def offset_number(self, args):
         """Handle numeric offset."""
         return Const(value=int(args[0]))
     
     def offset_variable(self, args):
         """Handle variable offset (e.g., i+j)."""
         return VariableRef(name=str(args[0]))
     ```
   - Semantic handler logic:
     - Case 1: `IDENTIFIER` → IndexExpression(base=id, offset=None)
     - Case 2: `IDENTIFIER "++" NUMBER` → IndexOffset(base=id, offset=BinaryOp("+", number), circular=True)
     - Case 3: `IDENTIFIER "--" NUMBER` → IndexOffset(base=id, offset=BinaryOp("-", number), circular=True)
     - Case 4: `IDENTIFIER "+" IDENTIFIER` → IndexOffset(base=id1, offset=VariableRef(id2), circular=False)
     - Case 5: Complex expressions (i+j+k) → Recursive expression tree

3. **Create IR IndexExpression nodes** (1 hour)
   - Open `src/ir/nodes.py`
   - Add `IndexOffset` IR node:
     ```python
     @dataclass
     class IndexOffset(IRNode):
         """Represents lead/lag indexing (i++1, i--2, i+j)."""
         base: str              # Base identifier (e.g., 'i', 't', 's')
         offset: IRNode         # Offset expression (Const, BinaryOp, VariableRef, etc.)
         circular: bool         # True for ++/--, False for +/-
         
         def __post_init__(self):
             """Validate IndexOffset node."""
             if not isinstance(self.base, str):
                 raise TypeError(f"base must be str, got {type(self.base)}")
             if not isinstance(self.offset, IRNode):
                 raise TypeError(f"offset must be IRNode, got {type(self.offset)}")
             if not isinstance(self.circular, bool):
                 raise TypeError(f"circular must be bool, got {type(self.circular)}")
     ```
   - Add IR traversal support (visitor pattern):
     ```python
     def visit_index_offset(self, node: IndexOffset):
         """Visit IndexOffset node."""
         self.generic_visit(node)
         # Traverse offset expression
         if node.offset:
             self.visit(node.offset)
     ```
   - Add string representation for debugging:
     ```python
     def __str__(self):
         op = "++" if self.circular and self.offset >= 0 else "--"
         return f"{self.base}{op}{abs(self.offset)}"
     ```

4. **Write unit tests for i++1, i--1 indexing** (1 hour)
   - Create `tests/test_indexing.py` (or extend existing)
   - Test cases from PLAN.md (lines 415-431):
     - `test_basic_indexing()` - `x(i)` → IndexExpression("i", None)
     - `test_i_plusplus_1()` - `x(i++1)` → IndexOffset("i", Const(1), circular=True)
     - `test_i_minusminus_5()` - `x(i--5)` → IndexOffset("i", BinaryOp("-", 0, Const(5)), circular=True)
     - `test_i_plus_j()` - `x(i+j)` → IndexOffset("i", VariableRef("j"), circular=False)
     - `test_i_plus_j_plus_k()` - Complex: `x(i+j+k)` → IndexOffset with BinaryOp tree
     - `test_negative_offsets()` - `x(i++(-3))` should work
     - `test_large_offsets()` - `x(i++100)` should work
     - `test_multiple_indices()` - `x(i++1, j--2)` should work
   - Edge case tests:
     - Boundary behavior (what happens at set edges?)
     - Zero offset: `x(i++0)` should equal `x(i)`
     - Negative offsets with circular: `x(i++(-1))` equivalent to `x(i--1)`
   - Target coverage: ≥80% for indexing code paths
   - Run tests after each function implementation (incremental testing)

**Deliverables:**
- Updated `src/grammar/gams.lark` - Arithmetic indexing grammar (CIRCULAR_LEAD, CIRCULAR_LAG tokens + index_expr rules)
- Updated `src/ir/semantic_handler.py` - Indexing semantic handler (6 new handler functions)
- Updated `src/ir/nodes.py` - IndexOffset node type with validation and traversal
- `tests/test_indexing.py` - Unit tests (≥80% coverage)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Grammar parses "i++1", "i--1", "i+j", "i-j" patterns
  - [ ] Semantic handler creates IndexOffset(base="i", offset=BinaryOp("+", 1), circular=True)
  - [ ] IR correctly represents arithmetic indexing
  - [ ] Unit tests cover edge cases (i++10, i--5, i+j+k, negative offsets, multiple indices)
  - [ ] Test coverage ≥80% for indexing code
  - [ ] All quality checks pass: `make typecheck && make lint && make format && make test`
  - [ ] **Early warning system passed:** Existing 4 models still parse (no regressions)
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_2/SPRINT_9/PLAN.md`
- [ ] Check off Day 3 in README.md
- [ ] Log Day 3 completion to CHANGELOG.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 9 Day 3: Advanced Indexing - Part 1 (i++1 Grammar & Semantic)" \
                --body "Completes Day 3 tasks from Sprint 9 PLAN.md

   ## Grammar Changes
   - Added CIRCULAR_LEAD (++) and CIRCULAR_LAG (--) tokens
   - Updated index_expr production for arithmetic indexing
   - Supports: i++1, i--1, i+j, i-j patterns
   
   ## Semantic Handler
   - Implemented 6 handler functions for lead/lag indexing
   - Creates IndexOffset IR nodes with circular flag
   - Handles numeric and variable offsets
   
   ## IR Representation
   - Added IndexOffset node to IR
   - Validation, traversal, and string representation
   
   ## Tests
   - XX unit tests covering edge cases
   - Coverage: XX% (target: ≥80%)
   - All tests pass ✅
   
   ## Regression Check
   - Existing 4 models still parse: [YES/NO]
   
   Ready for Day 4 (himmel16.gms validation)." \
                --base sprint9-advanced-features
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 340-463) - Day 3 detailed implementation plan
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 3) - i++1 research findings
- `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (9.1.1, 9.1.2, 9.1.3) - i++1 unknowns
- Task 3 grammar design: Token-level disambiguation, no conflicts

**Notes:**
- Effort: 4-5h (1-1.5h grammar + 2-2.5h semantic + 1h IR + 1h tests)
- Test incrementally: Run synthetic examples after grammar changes (don't wait for Day 4)
- Early warning: Re-run existing 4 models after each grammar change to catch regressions
- Mid-Day 3 checkpoint: Is grammar working for synthetic examples?
- Indexing is hot path in parse - keep semantic handler fast
- Performance: Indexing semantic handler reuses existing expression handling logic
