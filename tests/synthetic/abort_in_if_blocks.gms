$title Synthetic Test: abort$ in If-Blocks
$onText
Synthetic Test for abort$ Statements in If-Block Bodies

Purpose:
Validate that abort$ conditional statements work inside if-block bodies.

Feature:
Conditional abort inside if-blocks:
if(condition, abort$[condition] "message";);

Expected Result:
PARSE SUCCESS (already works per Task 5)

Pass Criteria:
- Parser succeeds without errors
- IR contains if-block with abort statement
- Condition correctly parsed in square brackets

Fail Criteria:
- Parse error on abort$ inside if-block
- IR missing if-block or abort statement
- Condition not parsed correctly

Minimal Example:
Minimum: scalar, if-block, abort$ with condition.

Dependencies:
- Basic scalar and if-block syntax
- abort$ statement support

Sprint:
9/10 (Already implemented per Task 5)

Reference:
- mingamma.gms lines 59, 62 use this pattern
- Task 5 verified abort$ in if-blocks works (Sprint 9 fix)
- This test validates existing functionality

$offText

* ===== TEST CODE BELOW =====

Scalar x /5/;

if(x > 0,
    abort$[x > 10] "Value too large";
);

* ===== END TEST CODE =====

* Verification Notes:
* - Should already pass (Sprint 9 implemented this)
* - Uses square bracket syntax: abort$[condition]
* - If fails, regression in abort$ handling
