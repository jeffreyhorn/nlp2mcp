$title Synthetic Test: Mixed Variable Bound Types
$onText
Synthetic Test for Mixed Variable Bound Types (.fx, .l, .lo, .up)

Purpose:
Validate that different bound types can coexist on same variable with different indices.

Feature:
Multiple bound types on indexed variable:
- .fx = fixed bound (sets both .lo and .up)
- .l = level/starting value
- .lo = lower bound
- .up = upper bound

Expected Result:
PARSE SUCCESS (after Sprint 10 bug fix)

Pass Criteria:
- Parser succeeds without errors
- Different bound types on different indices allowed
- No false conflicts between bound types
- Each index maintains its own bounds independently

Fail Criteria:
- Parse error on mixed bound syntax
- False positive conflicts between different indices
- Bounds incorrectly applied to all indices

Minimal Example:
Minimum: one set, one variable, different bound types on different indices.

Dependencies:
- Basic set and variable declarations
- Variable bound index expansion bug fix

Sprint:
10 (Bug fix)

Reference:
- himmel16.gms lines 57-68 mix .fx, .l, .lo, .up
- Task 3 found parser bug expands literal indices to ALL members
- This test validates mixed bounds work correctly

$offText

* ===== TEST CODE BELOW =====

Set i /i1*i3/;

Variable x(i);

x.fx('i1') = 0;
x.l('i2') = 0.5;
x.lo('i3') = 0;
x.up('i3') = 1;

* ===== END TEST CODE =====

* Verification Notes:
* - Different indices with different bound types
* - This is VALID GAMS syntax (himmel16.gms uses it)
* - If this passes, index expansion bug is fixed
