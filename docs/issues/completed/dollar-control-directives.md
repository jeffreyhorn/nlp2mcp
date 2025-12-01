# Issue: Dollar Control Directives

**GitHub Issue:** [#360](https://github.com/jeffreyhorn/nlp2mcp/issues/360)  
**Status:** In Progress (Phase 1 Complete)  
**Priority:** HIGH  
**Complexity:** HIGH (10-15h)  
**Impact:** 3 Tier 2 models (elec, gasoil, inscribedsquare)  
**Sprint:** Sprint 12 (Phase 1) / Sprint 13+ (Phases 2-4)

---

## Progress Update

### Phase 1: COMPLETE ✓ (Sprint 12, Commit 0cd64bf)

**Implemented Features:**
- `extract_set_directives()`: Extracts `$set varname value` directives
- `strip_set_directives()`: Strips `$set` lines from output
- Enhanced `%variable%` substitution for all `$set` variables
- Nested macro expansion (e.g., `$set np %n%+1`)

**Testing:**
- 19 unit tests in `test_dollar_set_directives.py` (all passing)
- elec.gms now parses past line 31 (was blocked by `%n%` and `%np%`)
- New failure at line 39 with `$(...)` syntax (different issue, out of scope)

**Quality Gates:** ✓ typecheck ✓ lint ✓ format ✓ test

**Remaining Phases:**
- Phase 2: `$macro` system (4h) - for inscribedsquare.gms
- Phase 3: `$batInclude` with arguments (2h) - for gasoil.gms  
- Phase 4: `$if`/`$else`/`$endif` conditionals (5h) - future-proofing

---

## Problem Description

GAMS uses compile-time dollar control directives (`$`) for conditional compilation, macro definitions, variable substitution, and parameterized includes. These preprocessing directives are essential for creating reusable, parameterized models.

Current parser strips some directives but doesn't implement their functionality:
- `$set`, `$if`, `$else`, `$endif` - Conditional compilation
- `%variable%` - Compile-time variable substitution
- `$macro` - Macro function definitions
- `$batInclude` with arguments - Parameterized file inclusion

---

## Affected Models

### 1. elec.gms (line 31)

**GAMS Syntax:**
```gams
$if not set n $set n 10
$set np %n%+1

Set i /1*%n%/;
Set ip /1*%np%/;
```

**Error:**
```
Error: Parse error at line 31, column 24: Unexpected character: '%'
```

**Blocker:** `%variable%` substitution not implemented. After stripping directives, `%n%` and `%np%` remain as invalid tokens.

---

### 2. gasoil.gms (line 48)

**GAMS Syntax:**
```gams
$batInclude copspart.inc nc4 21
```

**Error:**
```
Error: Parse error at line 48, column 4: Unexpected character: '1'
```

**Blocker:** `$batInclude` with arguments not supported. Arguments `nc4` and `21` should be passed to included file.

---

### 3. inscribedsquare.gms (line 34)

**GAMS Syntax:**
```gams
$set fx 1.0
$macro fx(t) %fx%*t

Variable x;
Equation eq;
eq.. x =e= fx(x);
```

**Error:**
```
Error: Parse error at line 34, column 14: Unexpected character: 's'
```

**Blocker:** `$macro` definitions not implemented. Macro `fx(t)` should expand inline.

---

## Root Cause Analysis

### Current Implementation (Partial)

**Preprocessor (src/ir/preprocessor.py):**
- `extract_conditional_sets()`: Extracts defaults from `$if not set` directives
- `expand_macros()`: Expands `%variable%` references (only for extracted defaults)
- `strip_conditional_directives()`: Removes `$if not set` lines
- `strip_unsupported_directives()`: Removes `$title`, `$ontext`, etc.

**Limitations:**
1. Only handles `$if not set` pattern, not general `$if` conditionals
2. Only substitutes variables from `$if not set`, not from `$set` directives
3. No support for `$macro` definitions
4. `$batInclude` arguments not processed
5. No support for `$else`, `$endif`, `$elseif`

---

## Implementation Requirements

### Feature 1: General `$set` Directive

**Syntax:**
```gams
$set varname value
$set n 10
$set path "c:\data\models"
```

**Behavior:**
- Store variable assignments in symbol table
- Values can be strings (quoted or unquoted) or numbers
- Later `$set` overrides earlier values

**Implementation:**
```python
def extract_set_directives(source: str) -> dict[str, str]:
    """Extract $set directives and return variable assignments."""
    pattern = r'\$set\s+(\w+)\s+(?:"([^"]*)"|(\S+))'
    macros = {}
    for match in re.finditer(pattern, source, re.IGNORECASE):
        var_name = match.group(1)
        value = match.group(2) or match.group(3)
        macros[var_name] = value
    return macros
```

---

### Feature 2: Conditional Compilation (`$if`, `$else`, `$endif`)

**Syntax:**
```gams
$if set n
    Set i /1*%n%/;
$else
    Set i /1*10/;
$endif

$if %n% > 5
    Parameter bigModel;
$endif
```

**Behavior:**
- Evaluate conditions at compile time
- Include/exclude code blocks based on condition
- Conditions: `set varname`, `not set varname`, `%var% > value`, etc.

**Implementation:**
- Parse conditional blocks into AST
- Evaluate conditions using variable symbol table
- Strip excluded blocks before parsing

**Complexity:** HIGH - requires conditional evaluation engine

---

### Feature 3: Enhanced `%variable%` Substitution

**Current:** Only substitutes variables from `$if not set` defaults  
**Required:** Substitute all `$set` variables

**Implementation:**
```python
def expand_all_macros(source: str, macros: dict[str, str]) -> str:
    """Expand all %variable% references."""
    result = source
    for var_name, value in macros.items():
        pattern = f"%{re.escape(var_name)}%"
        result = re.sub(pattern, value, result)
    return result
```

**Enhancement:** Already partially implemented, just need to merge with `$set` extraction.

---

### Feature 4: `$macro` Definitions

**Syntax:**
```gams
$macro fx(t) %scale%*t
$macro sum2(i,j,expr) sum(i, sum(j, expr))

x =e= fx(y);
total =e= sum2(i,j, data(i,j));
```

**Behavior:**
- Define function-like macros with parameters
- Inline expansion at usage sites
- Parameters are textual substitution (not evaluated)

**Implementation:**
```python
def extract_macros(source: str) -> dict[str, tuple[list[str], str]]:
    """Extract $macro definitions: name -> (params, body)."""
    pattern = r'\$macro\s+(\w+)\(([^)]*)\)\s+(.+)'
    macros = {}
    for match in re.finditer(pattern, source, re.IGNORECASE):
        name = match.group(1)
        params = [p.strip() for p in match.group(2).split(',')]
        body = match.group(3)
        macros[name] = (params, body)
    return macros

def expand_macro_calls(source: str, macros: dict) -> str:
    """Expand macro calls with argument substitution."""
    for name, (params, body) in macros.items():
        pattern = rf'{name}\(([^)]+)\)'
        def replacer(match):
            args = [a.strip() for a in match.group(1).split(',')]
            expanded = body
            for param, arg in zip(params, args):
                expanded = expanded.replace(param, arg)
            return expanded
        source = re.sub(pattern, replacer, source)
    return source
```

**Complexity:** MEDIUM - textual substitution with parameter mapping

---

### Feature 5: `$batInclude` with Arguments

**Syntax:**
```gams
$batInclude filename arg1 arg2 arg3
```

**Behavior:**
- Include file `filename`
- Pass arguments to included file
- Inside included file: `%1%` = arg1, `%2%` = arg2, etc.

**Implementation:**
```python
def preprocess_bat_include(file_path: Path, source: str) -> str:
    """Process $batInclude directives with argument substitution."""
    pattern = r'\$batInclude\s+(\S+)(.*)$'
    
    for match in re.finditer(pattern, source, re.IGNORECASE | re.MULTILINE):
        inc_file = match.group(1)
        args = match.group(2).split() if match.group(2) else []
        
        # Read included file
        inc_path = (file_path.parent / inc_file).resolve()
        inc_content = inc_path.read_text()
        
        # Substitute %1%, %2%, etc. with arguments
        for i, arg in enumerate(args, 1):
            inc_content = inc_content.replace(f'%{i}%', arg)
        
        # Replace $batInclude with expanded content
        source = source.replace(match.group(0), inc_content)
    
    return source
```

---

## Implementation Options

### Option A: Full Preprocessor Implementation (RECOMMENDED)

**Approach:** Implement complete dollar control directive system in preprocessor.

**Features:**
1. `$set` variable assignments
2. `$if`/`$else`/`$endif` conditionals
3. `%variable%` substitution (all variables)
4. `$macro` definitions and expansion
5. `$batInclude` with arguments

**Pros:**
- Complete GAMS compatibility
- Unlocks all 3 models + future models using these features
- Standard preprocessing approach

**Cons:**
- Significant implementation effort
- Conditional evaluation complexity

**Effort:** 10-15h
- `$set` extraction: 1h
- Enhanced `%variable%` substitution: 1h
- `$macro` system: 4h
- `$batInclude` with args: 2h
- `$if`/`$else`/`$endif` conditionals: 5h
- Testing: 2h

---

### Option B: Mock/Hardcoded Values

**Approach:** Hardcode specific values for known models, skip directive evaluation.

**Implementation:**
- elec.gms: Replace `%n%` with `10`, `%np%` with `11`
- inscribedsquare.gms: Inline expand `fx(t)` to `1.0*t`
- gasoil.gms: Copy copspart.inc inline with hardcoded args

**Pros:**
- Quick implementation (2-3h)
- Unlocks specific models

**Cons:**
- Not generalizable
- Breaks on parameter changes
- Technical debt

**Effort:** 2-3h (NOT RECOMMENDED)

---

### Option C: Partial Implementation (Incremental)

**Approach:** Implement features incrementally based on immediate needs.

**Phase 1:** `$set` + `%variable%` substitution (2h) - unlocks elec.gms  
**Phase 2:** `$macro` system (4h) - unlocks inscribedsquare.gms  
**Phase 3:** `$batInclude` args (2h) - unlocks gasoil.gms  
**Phase 4:** `$if` conditionals (5h) - future-proofing

**Effort:** 13h total, but can stop after each phase

---

## Recommendation

**Option C: Partial Implementation (Incremental)** - Start with Phase 1

**Rationale:**
1. **Immediate impact**: `$set` + `%variable%` unlocks elec.gms quickly (2h)
2. **Incremental value**: Each phase unlocks specific models
3. **Risk management**: Can stop if later phases prove too complex
4. **Foundation**: Builds infrastructure for full implementation

**Sprint 13 Plan:**
- **Phase 1** (2h): Implement `$set` + enhanced `%variable%` substitution → elec.gms ✓
- **Phase 2** (4h): Implement `$macro` system → inscribedsquare.gms ✓
- **Defer Phase 3-4** to Sprint 14+ based on priority

---

## Testing Requirements

### Unit Tests

**`$set` Directive:**
```gams
$set n 10
Set i /1*%n%/;
```
Expected: `Set i /1*10/;`

**`$macro` Definition:**
```gams
$set scale 2.5
$macro fx(t) %scale%*t
x =e= fx(y);
```
Expected: `x =e= 2.5*y;`

**`$batInclude` with Arguments:**
```gams
$batInclude file.inc arg1 arg2
```
file.inc:
```gams
Set i%1% /%2%/;
```
Expected: `Set iarg1 /arg2/;`

**Nested Substitution:**
```gams
$set n 10
$set np %n%+1
Set i /1*%np%/;
```
Expected: `Set i /1*10+1/;` → `Set i /1*11/;`

### Integration Tests

- elec.gms: `$set` + `%variable%`
- inscribedsquare.gms: `$macro` expansion
- gasoil.gms: `$batInclude` with arguments

---

## References

- GAMS Documentation: Dollar Control Options
- Failing models: `tests/fixtures/tier2_candidates/{elec,gasoil,inscribedsquare}.gms`
- Current preprocessor: `src/ir/preprocessor.py`
- Existing directive handling: `extract_conditional_sets()`, `expand_macros()`, `strip_conditional_directives()`
