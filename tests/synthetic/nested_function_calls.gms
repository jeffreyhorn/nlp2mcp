$title Synthetic Test: Nested Function Calls
$onText
Synthetic Test for Nested Function Calls

Purpose:
Validate that nested function calls work (function call as argument to another function).

Feature:
Nested function calls: sqrt(sqr(x)), log(exp(y)), etc.
Inner function result is argument to outer function.

Expected Result:
PARSE SUCCESS (after Sprint 10 implementation)

Pass Criteria:
- Parser succeeds without errors
- IR contains nested Call AST nodes
- Outer Call contains inner Call as argument
- Grammar supports arbitrary nesting depth

Fail Criteria:
- Parse error on nested function syntax
- IR has flat structure instead of nested
- Nesting depth limited incorrectly

Minimal Example:
Minimum: one parameter, one assignment with nested function calls.

Dependencies:
- Basic parameter declaration
- Function call grammar (to be implemented)

Sprint:
10 (To be implemented)

Reference:
- circle.gms line 48: sqrt(sqr(...) + sqr(...))
- maxmin.gms line 83: 1/max(ceil(sqrt(card(n)))-1,1) (depth 5!)
- Task 7 found max depth 5, 89% are depth ≤2

$offText

* ===== TEST CODE BELOW =====

Parameter p;

p = sqrt(sqr(5));

* ===== END TEST CODE =====

* Verification Notes:
* - Tests 2-level nesting (depth 2)
* - Grammar should support arbitrary depth through recursion
* - If this passes, nesting infrastructure works
