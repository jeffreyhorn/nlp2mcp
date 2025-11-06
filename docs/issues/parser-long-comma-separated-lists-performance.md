# Parser Performance Issue: Long Comma-Separated Lists Cause Timeouts

**GitHub Issue**: [#138](https://github.com/jeffreyhorn/nlp2mcp/issues/138)

## Status
**Open** - Performance limitation  
**Priority**: Medium  
**Component**: Parser (src/ir/parser.py)  
**Discovered**: 2025-11-06 during Sprint 5 Prep Task 8

## Description

The GAMS parser has performance issues with very long comma-separated lists in set element definitions. Lists with 100+ elements parse successfully but approach performance limits, while lists with 200+ elements can cause timeouts exceeding 30 seconds.

## Current Behavior

- **10 elements**: ~1.7s parse time ✓ Good
- **50 elements**: ~1.5-3.8s parse time ✓ Acceptable  
- **100 elements**: ~20-24s parse time ⚠️ Slow but works
- **200+ elements**: 30+ seconds, often timeout ❌ Fails

The parser appears to have exponential or quadratic time complexity with respect to list length.

## Expected Behavior

The parser should handle comma-separated lists efficiently with linear time complexity. A 1000-element list should parse in seconds, not minutes.

## Reproduction

### Test Case: Small (Works Fast)

Create `test_small.gms`:

```gams
Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10/
;

Variables x(i), obj;
Equations objdef;
objdef.. obj =e= sum(i, x(i));
Model test /all/;
Solve test using NLP minimizing obj;
```

Run:
```bash
time nlp2mcp test_small.gms -o output.gms
```

**Result**: ~1.7s ✓

### Test Case: Medium (Slow but Works)

Create `test_medium.gms` with 50 elements:

```gams
Sets
    i /i1, i2, i3, ..., i50/  # 50 elements
;

Variables x(i), obj;
Equations objdef;
objdef.. obj =e= sum(i, x(i));
Model test /all/;
Solve test using NLP minimizing obj;
```

Run:
```bash
time nlp2mcp test_medium.gms -o output.gms
```

**Result**: ~3.8s ⚠️

### Test Case: Large (Very Slow)

Create `test_large.gms` with 100 elements:

```gams
Sets
    i /i1, i2, i3, ..., i100/  # 100 elements
;

Variables x(i), obj;
Equations objdef;
objdef.. obj =e= sum(i, x(i));
Model test /all/;
Solve test using NLP minimizing obj;
```

Run:
```bash
time nlp2mcp test_large.gms -o output.gms
```

**Result**: ~24s ❌ Very slow

### Test Case: Extra Large (Timeout)

With 200+ elements, parsing often exceeds 30 seconds and times out.

## Performance Data

| Elements | Parse Time | Status |
|----------|-----------|--------|
| 10 | 1.7s | ✓ Good |
| 50 | 3.8s | ⚠️ Slow |
| 100 | 24s | ❌ Very Slow |
| 200+ | 30+ s | ❌ Timeout |

### Complexity Analysis

Approximate time complexity based on measurements:

```
T(10) = 1.7s
T(50) = 3.8s   # 2.2x for 5x elements
T(100) = 24s   # 6.3x for 2x elements
```

This suggests worse than linear complexity, possibly O(n²) or worse.

## Impact

**Moderate Impact:**
- **Large Models**: Cannot parse realistic large-scale models (1000+ elements)
- **Workaround Available**: Asterisk notation (if implemented) would help
- **Practical Limit**: Effectively limited to ~100 elements per set
- **User Experience**: Frustrating wait times even for medium models

**Combined with Asterisk Limitation**: This is a critical blocker for large models since:
1. Asterisk notation not supported (must use comma lists)
2. Long comma lists perform poorly
3. Result: Cannot handle large models at all

## Technical Analysis

### Likely Causes

1. **Backtracking in Parser**: Lark parser may be doing excessive backtracking on long lists

2. **Grammar Ambiguity**: The comma-separated list grammar may have ambiguities that cause exponential parsing paths

3. **Token Generation**: Lexer may be inefficient with long input streams

4. **AST Construction**: Building the AST for large lists may be O(n²)

5. **Memory Allocation**: Repeated memory allocations for list nodes

### Parser Grammar

Current grammar (approximate):

```lark
set_elements: element ("," element)*
element: IDENTIFIER
```

This should be O(n) but may interact poorly with other rules.

### Profiling Needed

To fix this issue, profiling is needed to identify the bottleneck:

```python
import cProfile
import pstats

cProfile.run('parse_gams_file("test_large.gms")', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

This would identify which parsing functions are taking the most time.

## Related Issues

- **Asterisk notation not supported**: Would reduce need for long lists
- **Parser may have general performance issues**: Could affect other constructs

## Suggested Fixes

### Short Term: Optimization

1. **Profile the Parser**: Identify specific bottleneck
2. **Optimize Grammar**: Eliminate backtracking and ambiguity
3. **Use Lalr Parser**: Switch from Earley to LALR(1) if possible (much faster)
4. **Streaming Parsing**: Parse large lists iteratively

### Medium Term: Asterisk Notation

Implement asterisk notation support (see separate issue), which would:
- Reduce list lengths in source: `/i1*i1000/` instead of 1000 elements
- Parse-time expansion is O(1) for the notation
- Generate elements programmatically: O(n) but much faster

### Long Term: Lazy Evaluation

For very large sets, consider lazy evaluation:
- Don't expand `/i1*i100000/` into 100K elements immediately
- Keep as range representation
- Expand only when iterating in operations

## Workarounds

### Current Workaround: Limit Model Size

Keep models under 100 elements per set. This is the current practical limit.

### Future Workaround: Asterisk Notation

Once implemented, this will be the primary solution:

```gams
Sets
    i /i1*i1000/  # Fast to parse, generates 1000 elements
;
```

### Alternative: Multiple Small Sets

Break large sets into smaller chunks:

```gams
Sets
    i1_100 /i1*i100/
    i101_200 /i101*i200/
    i /i1*i200/  # Union (if supported)
;
```

But this requires complex model restructuring.

## Suggested Fix Priority

**Medium Priority:**
- Blocks large model testing
- Has workaround (limit model size) but unsatisfactory
- Critical when combined with asterisk limitation
- Affects user experience significantly

**Recommend**: Fix together with asterisk notation support for maximum impact.

## Testing Requirements

When fixing, add performance regression tests:

1. **Baseline Performance**:
   ```python
   def test_parser_performance_baseline():
       # 10 elements should parse in < 2s
       # 50 elements should parse in < 5s
       # 100 elements should parse in < 10s
   ```

2. **Scaling Tests**:
   ```python
   def test_parser_scales_linearly():
       times = []
       for n in [10, 50, 100, 500]:
           time = measure_parse_time(n)
           times.append(time)
       
       # Check near-linear scaling
       assert times[1] / times[0] < 10  # 5x elements, <10x time
       assert times[2] / times[1] < 5   # 2x elements, <5x time
   ```

3. **Large Model Tests**:
   ```python
   @pytest.mark.slow
   def test_parser_handles_1000_elements():
       # 1000 elements should parse in < 30s
       assert parse_time < 30
   ```

4. **Memory Tests**:
   ```python
   def test_parser_memory_usage_scales_linearly():
       # Memory should scale linearly with list length
       memory_10 = measure_memory(10)
       memory_100 = measure_memory(100)
       assert memory_100 / memory_10 < 15  # Allow some overhead
   ```

## Benchmarking

Create benchmark suite in `tests/benchmarks/test_parser_performance.py`:

```python
import pytest
import time

class TestParserPerformance:
    @pytest.mark.parametrize("size", [10, 50, 100, 200, 500])
    def test_comma_list_scaling(self, size):
        """Test parser performance with various list sizes."""
        model = generate_model_with_n_elements(size)
        
        start = time.time()
        parse_result = parse_gams(model)
        elapsed = time.time() - start
        
        # Record for analysis
        print(f"Size {size}: {elapsed:.2f}s")
        
        # Assert reasonable performance
        max_time = size * 0.05  # 50ms per element
        assert elapsed < max_time
```

## Investigation Steps

1. **Profile current parser** on 10, 50, 100 element lists
2. **Identify bottleneck**: Lexer, parser rules, AST construction?
3. **Check parser algorithm**: Is it Earley (slow) or LALR (fast)?
4. **Review grammar** for ambiguities causing backtracking
5. **Benchmark fixes** to verify improvement

## Expected Improvements

With proper optimization:

| Elements | Current | Target | Improvement |
|----------|---------|--------|-------------|
| 10 | 1.7s | 0.5s | 3.4x |
| 50 | 3.8s | 1.0s | 3.8x |
| 100 | 24s | 2.0s | 12x |
| 1000 | N/A | 10s | New capability |

Target: **Linear O(n) complexity** with low constant factor.

## References

- **Sprint 5 Prep Task 8**: Performance issue discovered during test model generation
- **Lark Documentation**: Parser performance and optimization
- **Parser Algorithm**: Earley vs LALR performance characteristics
- **Related Issue**: Asterisk notation support would mitigate this issue
