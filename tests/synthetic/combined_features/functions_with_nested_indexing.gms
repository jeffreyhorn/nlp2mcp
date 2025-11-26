$ontext
Feature Interaction Test: Function Calls + Nested Indexing

Purpose: Test that function calls work correctly with nested index expressions
Risk Level: HIGH
Expected Behavior:
  - Parser should accept function calls with nested indices in arguments
  - Call node structure should be preserved
  - Nested indexing should work inside function arguments

Rationale:
  Both features involve complex expression parsing. Function calls introduce Call
  nodes, while nested indexing creates IndexedAccess nodes with subset expressions.
  Risk: Parser may fail to handle nested index inside function argument.

Sprint: 11 Prep
Date: 2025-11-26
$offtext

Sets
    i "Main index" / i1*i5 /
    j "Secondary index" / j1*j3 /
    subset(i) "Active subset" / i1, i3, i5 /
    filter(j) "Filtered values" / j1, j2 /;

Parameters
    data(i,j) "Data matrix"
    single(i) "Single-indexed data"
    result1 "Result with single-nested index"
    result2 "Result with double-nested index"
    result3 "Result with multiple args";

* Populate data
data(i,j) = ord(i) * ord(j);
single(i) = ord(i) * 10;

* Test 1: Function with single-level nested index
* Pattern: sqrt(data(subset(i), j))
* Expected: Parse succeeds, Call node with nested index in first argument
result1 = sqrt(single(subset(i)));

* Test 2: Function with double-nested index
* Pattern: exp(data(subset(i), filter(j)))
* Expected: Parse succeeds, Call node with doubly-nested indices
result2 = exp(sum((subset(i), filter(j)), data(i,j)));

* Test 3: Function with multiple arguments, one nested
* Pattern: power(base, exponent(subset(i)))
* Expected: Parse succeeds, second argument has nested index
result3 = power(2, single(subset(i)));

Display result1, result2, result3;
