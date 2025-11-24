$title Synthetic Test: Equation Attributes
$onText
Synthetic Test for Equation Attributes (.l, .m)

Purpose:
Validate that equation attribute access (.l for level, .m for marginal/dual)
works in isolation.

Feature:
Equation attributes allow accessing solution values:
- .l = level/primal value of equation
- .m = marginal/dual value of equation

Expected Result:
PARSE SUCCESS

Pass Criteria:
- Parser succeeds without errors
- IR contains parameter assignment with equation attribute access
- Attribute (.l or .m) correctly parsed on equation identifier

Fail Criteria:
- Parse error on equation attribute syntax
- IR missing attribute access node
- Incorrect attribute type

Minimal Example:
This test uses minimum declarations: one variable, one equation, one parameter.
Tests both .l and .m attributes.

Dependencies:
- Basic variable declaration
- Basic equation definition
- Basic parameter declaration

Sprint:
9 (Implemented)

Reference:
- Sprint 9 implemented equation attributes
- mingamma.gms was expected to use these (but doesn't)
- This test validates the feature works

$offText

* ===== TEST CODE BELOW =====

Variable x;

Equation obj;

obj.. x =e= 0;

Parameter level, dual;

level = obj.l;
dual = obj.m;

* ===== END TEST CODE =====

* Verification Notes:
* - Tests both .l (level) and .m (marginal) attributes
* - If this passes, equation attributes work correctly
* - Proves feature implementation is correct
