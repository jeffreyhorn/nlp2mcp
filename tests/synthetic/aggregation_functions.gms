$title Synthetic Test: Aggregation Functions in Parameters
$onText
Synthetic Test for Aggregation Functions (smin/smax) in Parameter Assignments

Purpose:
Validate that aggregation functions (smin, smax, sum) work in parameter assignments.

Feature:
Aggregation functions iterate over sets:
- smin(i, expr(i)) = minimum value of expr over set i
- smax(i, expr(i)) = maximum value of expr over set i
- sum(i, expr(i)) = sum of expr over set i

Expected Result:
PARSE SUCCESS (after Sprint 10 implementation)

Pass Criteria:
- Parser succeeds without errors
- IR contains parameter with aggregation FunctionCall
- FunctionCall has set reference and expression arguments

Fail Criteria:
- Parse error on aggregation function syntax
- IR missing FunctionCall or incorrect argument structure
- Set reference not properly parsed

Minimal Example:
Minimum declarations: one set, one parameter with data, one parameter with aggregation.

Dependencies:
- Basic set and parameter declarations
- Function call grammar (to be implemented)

Sprint:
10 (To be implemented)

Reference:
- circle.gms uses smin(i, x(i)) and smax(i, y(i)) in lines 40-43
- This is PRIMARY blocker for circle.gms
- Task 7 cataloged smin/smax as Aggregation category

$offText

* ===== TEST CODE BELOW =====

Set i /i1*i3/;

Parameter x(i) /i1 1, i2 2, i3 3/;

Parameter xmin, xmax;

xmin = smin(i, x(i));
xmax = smax(i, x(i));

* ===== END TEST CODE =====

* Verification Notes:
* - Tests both smin and smax aggregation functions
* - If this passes, aggregation in parameters works
* - Critical for unlocking circle.gms
