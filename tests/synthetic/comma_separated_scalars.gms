$title Synthetic Test: Comma-Separated Scalars with Inline Values
$onText
Synthetic Test for Comma-Separated Scalar Declarations with Mixed Inline Values

Purpose:
Validate that comma-separated scalar declarations with mixed inline values work.

Feature:
Multiple scalars in one statement with some having inline values:
Scalar x1 /1.0/, x2, x3 /3.0/;

Expected Result:
PARSE SUCCESS (after Sprint 10 implementation)

Pass Criteria:
- Parser succeeds without errors
- IR contains 3 scalars
- x1 has value 1.0, x2 undefined, x3 has value 3.0

Fail Criteria:
- Parse error on mixed inline values
- IR missing scalars or incorrect values
- All scalars get same value (incorrect)

Minimal Example:
Minimum: single Scalar statement with comma-separated list and mixed inline values.

Dependencies:
- Basic scalar declaration grammar
- Inline value syntax

Sprint:
10 (To be implemented)

Reference:
- mingamma.gms lines 30-38 uses this pattern (SECONDARY blocker)
- Task 6 found this is VALID GAMS syntax per documentation
- Grammar needs scalar_list update to support inline values

$offText

* ===== TEST CODE BELOW =====

Scalar x1 /1.0/, x2, x3 /3.0/;

* ===== END TEST CODE =====

* Verification Notes:
* - Tests mixing scalars with and without inline values
* - This is mingamma.gms secondary blocker
* - If this passes, mingamma should reach 100%
