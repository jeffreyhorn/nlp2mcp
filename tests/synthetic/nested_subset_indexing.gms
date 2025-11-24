$title Synthetic Test: Nested/Subset Indexing (DEFERRED)
$onText
Synthetic Test for Nested/Subset Indexing in Equation Domains

Purpose:
Validate that subset domain restrictions in equation declarations work.

Feature:
Subset domains restrict equations to subset members:
- Set low(n,n) declares 2D subset
- low(n,nn) = ord(n) > ord(nn); assigns subset
- Equation test(low(n,nn)) restricts equation to subset

Expected Result:
PARSE FAILURE (deferred to Sprint 11)

Pass Criteria (when implemented):
- Parser succeeds without errors
- IR contains equation with subset domain restriction
- Subset reference resolved correctly
- Indices inferred from subset dimensionality

Fail Criteria:
- Parse error on subset domain syntax
- IR missing subset reference
- Incorrect index binding or resolution

Minimal Example:
Minimum: one set, subset declaration, alias, subset assignment, equation with subset domain.

Dependencies:
- Basic set, alias, equation syntax
- Subset indexing grammar (NOT IMPLEMENTED)

Sprint:
11+ (Deferred per Task 8 recommendation)

Reference:
- maxmin.gms uses this extensively (lines 51, 53, 55)
- Task 8 analyzed: 10-14h, HIGH complexity, LOW ROI
- DEFER decision: Focus on higher ROI features in Sprint 10

$offText

* ===== TEST CODE BELOW =====

Set i /i1*i3/;

Set low(i,i);

Alias (i,j);

low(i,j) = ord(i) > ord(j);

Equation test(low(i,j));

test(low(i,j)).. 1 =e= 1;

* ===== END TEST CODE =====

* Verification Notes:
* - This will FAIL until Sprint 11+ implementation
* - Test marked as SKIP in pytest
* - Kept for future validation when feature implemented
* - Complexity: 9/10, deferred for good reason
