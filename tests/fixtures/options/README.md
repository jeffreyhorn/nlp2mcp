# Option Statement Fixtures

This directory contains test fixtures for GAMS option statement features (Sprint 8 Day 2).

## Purpose

These fixtures test the parser's ability to handle option statements with integer values. Sprint 8 implements a mock/store approach where options are parsed and stored in the AST but not semantically processed.

## Fixture Structure

Each fixture consists of:
- `*.gms` - Input GAMS file with specific option pattern
- `expected_results.yaml` - Expected parse results and AST structure

## Fixtures

### 01_single_integer.gms
**Pattern:** Single integer option  
**Code:** `option limrow = 0;`  
**Purpose:** Test basic option statement with single integer value  
**Expected:** Parse successfully, store option ("limrow", 0)

### 02_multiple_options.gms
**Pattern:** Multiple options in one statement  
**Code:** `option limrow = 0, limcol = 0;`  
**Purpose:** Test comma-separated multiple options  
**Expected:** Parse successfully, store both options

### 03_decimals_option.gms
**Pattern:** Decimals display option  
**Code:** `option decimals = 8;`  
**Purpose:** Test decimals option (different option type)  
**Expected:** Parse successfully, store option ("decimals", 8)

### 04_placement.gms
**Pattern:** Options in different locations  
**Code:** Options before declarations, after declarations, and after code  
**Purpose:** Test option statement placement flexibility  
**Expected:** Parse successfully, store all 3 option statements

### 05_mhw4dx_pattern.gms
**Pattern:** Real GAMSLib pattern from mhw4dx.gms  
**Code:** Simplified excerpt with `option limCol = 0, limRow = 0;` and `option decimals = 8;`  
**Purpose:** Ensure real-world pattern support (validates mhw4dx unlock)  
**Expected:** Parse successfully, store both option statements with case preserved

## Usage

### Parse all option fixtures
```bash
for f in tests/fixtures/options/*.gms; do 
    python -m src.cli parse "$f"
done
```

### Run fixture validation tests
```bash
pytest tests/parser/test_option_statements.py -v
```

### Parse individual fixture
```python
from src.ir.parser import parse_model_file

model = parse_model_file('tests/fixtures/options/01_single_integer.gms')
print(f"Option statements: {len(model.option_statements)}")
for opt_stmt in model.option_statements:
    print(f"  Options: {opt_stmt.options}")
```

## Expected Results

All 5 fixtures should parse successfully:
- **Total:** 5 fixtures
- **Passing:** 5 (100%)
- **Failing:** 0

See `expected_results.yaml` for detailed AST structure expectations.

## Sprint 8 Scope

**Implemented:**
- ✅ Integer option values (0-8 range)
- ✅ Single and multiple option statements
- ✅ Option names: limrow, limcol, decimals
- ✅ Case-insensitive `option`/`options` keywords
- ✅ Case-preserved option names
- ✅ Mock/store approach (no semantic processing)

**Not Implemented (Future):**
- ❌ Boolean option values (on/off) - grammar exists but not used in GAMSLib
- ❌ String option values
- ❌ Per-identifier options (`:` operator)
- ❌ Projection operators (`<`, `<=`, `>`)
- ❌ Semantic validation (option name validation)
- ❌ Semantic effects (display control, solver settings)

## GAMSLib Validation

These fixtures directly support mhw4dx.gms unlock:
- mhw4dx.gms uses `option limCol = 0, limRow = 0;` (line 37)
- mhw4dx.gms uses `option decimals = 8;` (line 47)
- Fixture 05 contains the exact patterns from mhw4dx.gms

**Parse Rate Impact:**
- Before Sprint 8: 20% (2/10 models: mhw4d, rbrock)
- After Sprint 8 Day 1-2: Target 30% (3/10 models: +mhw4dx)
  - Note: mhw4dx has secondary blocker (elseif statements) that may prevent full unlock in Sprint 8

## Cross-References

- **Research:** `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md`
- **Strategy:** `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md`
- **Implementation:** `src/ir/parser.py` (_handle_option_stmt)
- **Grammar:** `src/gams/gams_grammar.lark` (option_stmt rules)
- **AST:** `src/ir/symbols.py` (OptionStatement dataclass)
- **Tests:** `tests/parser/test_option_statements.py`
