$title Synthetic Test: i++1 Lead/Lag Indexing
$onText
Synthetic Test for i++1 Lead/Lag Indexing

Purpose:
Validate that i++1 and i--1 lead/lag indexing syntax works in isolation.

Feature:
Lead/lag indexing allows referencing next (i++1) or previous (i--1) elements
in a set during equation definitions.

Expected Result:
PARSE SUCCESS

Pass Criteria:
- Parser succeeds without errors
- IR contains equation with lead/lag index references
- i++1 correctly represents reference to next element in set
- i--1 correctly represents reference to previous element in set

Fail Criteria:
- Parse error on i++1 or i--1 syntax
- IR missing equation or index references
- Incorrect index resolution

Minimal Example:
This test uses the absolute minimum: one set, one variable, one equation.
No parameters, no solve, no model declaration - just the feature itself.

Dependencies:
- Basic set declaration
- Basic variable declaration
- Basic equation definition

Sprint:
9 (Implemented)

Reference:
- himmel16.gms uses i++1 in line 48
- Sprint 9 implemented this feature
- This test validates it works in isolation

$offText

* ===== TEST CODE BELOW =====

Set i /i1*i3/;

Variable x(i);

Equation test(i);

test(i).. x(i) =e= x(i++1);

* ===== END TEST CODE =====

* Verification Notes:
* - This minimal test proves i++1 syntax works
* - If this passes, feature is correctly implemented
* - If himmel16.gms still fails, the issue is a secondary blocker
