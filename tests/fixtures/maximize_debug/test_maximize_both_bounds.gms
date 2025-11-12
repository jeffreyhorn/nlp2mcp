$title Maximize with Both Lower and Upper Bounds
$ontext
Test: Maximize with both bounds
Purpose: Test both bound multipliers simultaneously
Expected solution: x = 10, obj = 10 (should hit upper bound)
Bug symptom: Both piL_x and piU_x will have wrong signs in stationarity
$offtext

Variables x, obj;

* Set both bounds
x.lo = 5;
x.up = 10;

Equations objdef;

* Simple linear objective: maximize x
objdef.. obj =e= x;

Model test /all/;

* Solve maximizing - should push to upper bound
Solve test using NLP maximizing obj;

Display x.l, obj.l;

* Verify solution
parameter expected_x;
expected_x = 10;

abort$(abs(x.l - expected_x) > 1e-6) "FAILED: x should be 10 at upper bound";
