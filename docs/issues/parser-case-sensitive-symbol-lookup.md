# Parser Limitation: Case-Sensitive Symbol Lookup

**GitHub Issue**: [#373](https://github.com/jeffreyhorn/nlp2mcp/issues/373)

## Status
**Open** - Parser limitation  
**Priority**: Medium  
**Component**: Parser (src/ir/parser.py), ModelIR (src/ir/model_ir.py)  
**Discovered**: 2025-12-02 during Issue #139 fix (multi-dimensional parameters)

## Description

The GAMS parser uses case-sensitive symbol lookup, but GAMS itself is case-insensitive. This causes parse failures when models use different casing for the same symbol (e.g., declaring `data_f` but referencing `data_F`).

## Current Behavior

When a model declares a symbol with one casing and references it with different casing, the parser fails with:

```
Error: Undefined symbol 'data_F' with indices ('f', "'sulfur'") referenced [context: assignment] [domain: ('f',)]
  req_sulfur(f)     = data_F(f,'sulfur');
                      ^

Suggestion: Declare 'data_F' as a variable, parameter, or set before using it
```

## Expected Behavior

The parser should treat symbol names case-insensitively, matching GAMS behavior:
- `data_f`, `data_F`, `DATA_F`, `Data_F` should all refer to the same symbol
- Symbol storage should normalize to a canonical form (e.g., lowercase or first declaration casing)
- Symbol lookup should be case-insensitive

## Reproduction

### Affected Model: haverly.gms

The Tier 2 model `haverly.gms` demonstrates this issue:

**Line 38:** Declaration (lowercase)
```gams
Table data_f(f,*) 'final product data'
        price  sulfur  demand
finalX       9     2.5     100
finalY      15     1.5     200;
```

**Lines 49-50, 77:** Usage (uppercase F)
```gams
req_sulfur(f)     = data_F(f,'sulfur');
demand(f)         = data_F(f,'demand');
...
incomedef..   income   =e= sum(f, data_F(f,'price')*final(f));
```

### Minimal Test Case

```gams
Sets
    i /i1, i2/
;

Parameters
    myParam(i) / i1 1.0, i2 2.0 /
;

Variables
    x(i)
;

Equations
    balance(i)
;

balance(i).. x(i) =e= MYPARAM(i);  # Different case

Model test /all/;
Solve test using NLP minimizing x;
```

**Current Result**: Parse error - "Undefined symbol 'MYPARAM'"  
**Expected Result**: Should reference `myParam`

## Impact

**Medium Impact:**
- **Real GAMS Models**: Valid GAMS models fail to parse
- **User Experience**: Confusing errors for valid GAMS syntax
- **Tier 2 Coverage**: Blocks haverly.gms (pooling problem)
- **Portability**: Models written for GAMS don't work without modification

**Workaround Available**: Yes - manually fix casing in model files (but breaks GAMS compatibility)

## Technical Details

### Current Implementation

Symbol storage uses Python dictionaries with exact case matching:

```python
@dataclass
class ModelIR:
    sets: dict[str, SetDef] = field(default_factory=dict)
    aliases: dict[str, AliasDef] = field(default_factory=dict)
    params: dict[str, ParameterDef] = field(default_factory=dict)
    variables: dict[str, VariableDef] = field(default_factory=dict)
    equations: dict[str, EquationDef] = field(default_factory=dict)
    
    def add_param(self, p: ParameterDef) -> None:
        self.params[p.name] = p  # Exact case storage
```

Symbol lookup also uses exact case:

```python
# In parser symbol resolution
if symbol_name not in self.model.params:
    raise error(f"Undefined symbol '{symbol_name}'")
```

### Proposed Implementation

**Option 1: Normalize to Lowercase (Simplest)**

```python
@dataclass
class ModelIR:
    # Internal storage uses lowercase keys
    _sets: dict[str, SetDef] = field(default_factory=dict)
    _params: dict[str, ParameterDef] = field(default_factory=dict)
    # ... etc
    
    # Store original casing for display/output
    _original_names: dict[str, str] = field(default_factory=dict)
    
    def add_param(self, p: ParameterDef) -> None:
        canonical = p.name.lower()
        self._params[canonical] = p
        if canonical not in self._original_names:
            self._original_names[canonical] = p.name  # Keep first declaration
    
    def get_param(self, name: str) -> ParameterDef | None:
        return self._params.get(name.lower())
```

**Option 2: Case-Insensitive Dict Wrapper**

```python
class CaseInsensitiveDict(dict):
    def __init__(self):
        super().__init__()
        self._key_map = {}  # lowercase -> original
    
    def __setitem__(self, key: str, value):
        canonical = key.lower()
        super().__setitem__(canonical, value)
        if canonical not in self._key_map:
            self._key_map[canonical] = key
    
    def __getitem__(self, key: str):
        return super().__getitem__(key.lower())
    
    def __contains__(self, key: str):
        return super().__contains__(key.lower())
    
    def get_original_name(self, key: str) -> str:
        return self._key_map.get(key.lower(), key)
```

**Option 3: Hybrid - Preserve Case Display**

Store symbols with their original casing but lookup case-insensitively:
- Display names use first declaration casing
- Internal lookup normalizes to lowercase
- Error messages use original casing

### Areas Requiring Changes

1. **ModelIR Storage** (src/ir/model_ir.py)
   - Symbol dictionaries: sets, aliases, params, variables, equations
   - Add/get methods for case-insensitive lookup
   - Preserve original casing for output

2. **Parser Symbol Lookup** (src/ir/parser.py)
   - `_resolve_set_def()` - set lookups
   - `_make_symbol()` - variable/parameter references
   - `_ensure_set_exists()` - set validation
   - `_verify_member_in_domain()` - set member validation
   - All symbol resolution code

3. **Symbol Declaration** (src/ir/parser.py)
   - `_handle_sets_block()` - set declarations
   - `_handle_params_block()` - parameter declarations
   - `_handle_vars_block()` - variable declarations
   - `_handle_equations_block()` - equation declarations
   - Alias handling

4. **Code Generation** (src/emit/emit_gams.py)
   - Use original casing when emitting GAMS code
   - Preserve readability

5. **Set Member Lookup**
   - Set members should also be case-insensitive
   - `SetDef.members` lookup needs case-insensitive matching

### Edge Cases to Consider

1. **First Declaration Wins**:
   ```gams
   Parameter myParam;
   Parameter MYPARAM;  # Should be same symbol, not redeclaration
   ```

2. **Error Messages**:
   ```gams
   Parameter myParam;
   x = MYPARAM + 1;  # Error should show "Did you mean 'myParam'?"
   ```

3. **Set Members**:
   ```gams
   Set i /i1, i2/;
   Parameter a(i) / I1 1.0, I2 2.0 /;  # Should work
   ```

4. **Aliases**:
   ```gams
   Set i /i1, i2/;
   Alias (J, i);  # j and J should both refer to i
   ```

5. **Reserved Keywords**:
   - GAMS keywords (Set, Parameter, etc.) are case-insensitive
   - Already handled by grammar/lexer

## GAMS Specification

From GAMS documentation:
> "GAMS is case-insensitive. The names MyParameter, MYPARAMETER, and myparameter all refer to the same symbol."

## Testing Requirements

When implementing, add tests for:

1. **Basic Case Variations**:
   ```gams
   Parameter x; x = 1;
   Parameter y; Y = 2;
   Parameter z; Z = z + X + y;  # All should resolve
   ```

2. **Cross-Reference Cases**:
   ```gams
   Parameter cost(i);
   balance(i).. x(i) =e= COST(i);  # Different case reference
   ```

3. **Set Members**:
   ```gams
   Set i /i1, i2/;
   Parameter a(i) / I1 1.0, i2 2.0 /;  # Mixed case members
   ```

4. **Duplicate Detection**:
   ```gams
   Parameter x;
   Parameter X;  # Should NOT be redeclaration error
   ```

5. **Alias Resolution**:
   ```gams
   Set i;
   Alias (J, i);
   Parameter a(j);  # Lowercase j should work
   ```

6. **Error Messages**:
   ```gams
   Parameter myParam;
   x = myParrm;  # Typo - should suggest 'myParam'
   ```

7. **Table Names**:
   ```gams
   Table data(i,j);
   x = DATA(i,j);  # Should work
   ```

8. **Integration Test**:
   - Parse haverly.gms successfully
   - Verify all symbols resolve correctly

## Related Issues

- Issue #139: Multi-dimensional parameters (where this was discovered)
- Future: Set member case-insensitivity
- Future: Fuzzy matching for typos (suggest similar names)

## Suggested Fix Priority

**Medium Priority:**
- Not blocking most models (only those with inconsistent casing)
- Valid GAMS models should work without modification
- Improves GAMS compatibility significantly
- Relatively contained change (symbol storage/lookup)

## Implementation Recommendation

**Recommended Approach**: Option 1 (Normalize to Lowercase)

**Pros**:
- Simplest to implement
- Matches GAMS internal behavior
- Clear canonical form
- Easy to debug

**Cons**:
- Need to preserve original casing for output
- Requires changes throughout codebase

**Implementation Steps**:
1. Add case-insensitive lookup methods to ModelIR
2. Update all symbol declaration code to use lowercase keys
3. Update all symbol lookup code to use lowercase
4. Preserve original casing in metadata for display
5. Add comprehensive tests
6. Verify haverly.gms parses successfully
7. Run full test suite

**Estimated Complexity**: Medium (4-6 hours)
- Symbol storage refactoring: 2 hours
- Parser updates: 2 hours
- Testing and edge cases: 2 hours

## Alternative: Document as Limitation

If not implementing immediately, document that:
- Models must use consistent casing
- Provide tool to normalize casing in GAMS files
- Add better error message: "Did you mean 'data_f' (declared on line 38)?"

## References

- **GAMS Documentation**: Case-insensitivity specification
- **haverly.gms**: Real-world example (Tier 2 model)
- **Issue #139**: Where this limitation was discovered
