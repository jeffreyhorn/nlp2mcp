$title Synthetic Test: Variable Level Bounds
$onText
Synthetic Test for Variable Level (.l) Assignments

Purpose:
Validate that variable level bound assignments work for indexed variables.

Feature:
Variable level bounds (.l) set starting values for solver:
- x.l('i1') = 1 sets starting value for x at index i1

Expected Result:
PARSE SUCCESS (after Sprint 10 bug fix)

Pass Criteria:
- Parser succeeds without errors
- IR contains level bounds for specific indices
- Multiple .l assignments on different indices allowed
- No spurious "conflicting level bound" errors

Fail Criteria:
- Parse error on .l syntax
- IR missing level bound assignments
- False positive conflict errors for different indices

Minimal Example:
Minimum: one set, one variable, multiple .l assignments on different indices.

Dependencies:
- Basic set and variable declarations
- Variable bound index expansion bug fix

Sprint:
10 (Bug fix)

Reference:
- himmel16.gms line 63 triggers "conflicting level bound" error
- Task 3 identified bug in _expand_variable_indices
- This test validates the fix works

$offText

* ===== TEST CODE BELOW =====

Set i /i1*i2/;

Variable x(i);

x.l('i1') = 1;
x.l('i2') = 2;

* ===== END TEST CODE =====

* Verification Notes:
* - Two different indices should NOT conflict
* - If this passes, bug fix works correctly
* - himmel16.gms uses this pattern extensively
