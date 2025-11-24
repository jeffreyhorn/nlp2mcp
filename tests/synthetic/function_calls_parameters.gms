$title Synthetic Test: Function Calls in Parameters
$onText
Synthetic Test for Function Calls in Parameter Assignments

Purpose:
Validate that function call syntax works in parameter assignments.

Feature:
Function calls in parameter assignments allow initializing parameters
with computed values: p = uniform(1,10), p = sqrt(2), etc.

Expected Result:
PARSE SUCCESS (after Sprint 10 implementation)

Pass Criteria:
- Parser succeeds without errors
- IR contains parameter with FunctionCall AST node
- FunctionCall has correct func name and arguments

Fail Criteria:
- Parse error on function call syntax in assignment
- IR missing parameter or FunctionCall node
- Incorrect function name or arguments

Minimal Example:
This test uses absolute minimum: one parameter, one assignment with function call.
No sets, variables, or equations - just parameter with function call.

Dependencies:
- Basic parameter declaration
- Function call grammar (to be implemented)

Sprint:
10 (To be implemented)

Reference:
- circle.gms uses uniform(1,10) in lines 25-26
- Task 7 found 19 functions across 6 categories
- This test validates basic function call parsing

$offText

* ===== TEST CODE BELOW =====

Parameter p;

p = uniform(1,10);

* ===== END TEST CODE =====

* Verification Notes:
* - Tests most basic function call: uniform with 2 constant args
* - If this passes, function call infrastructure works
* - More complex tests: aggregation_functions.gms, nested_function_calls.gms
