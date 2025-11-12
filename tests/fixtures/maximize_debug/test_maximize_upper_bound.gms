$title Maximize with Upper Bound Only
$ontext
Test: Maximize with upper bound
Purpose: Isolate the bound multiplier sign bug
Expected solution: x = 10, obj = 10 (x should hit upper bound)
Bug symptom: Wrong solution or PATH failure due to incorrect piU_x sign
KKT condition: Should have stat_x.. ... - piU_x =E= 0 (subtract upper multiplier)
Current bug: Generates stat_x.. ... + piU_x =E= 0 (adds upper multiplier)
$offtext

Variables x, obj;

* Set upper bound - x can't go above 10
x.up = 10;

Equations objdef;

* Simple linear objective: maximize x
objdef.. obj =e= x;

Model test /all/;

* Solve maximizing - should push x to upper bound
Solve test using NLP maximizing obj;

Display x.l, obj.l;

* Verify expected solution
parameter expected_x;
expected_x = 10;

abort$(abs(x.l - expected_x) > 1e-6) "FAILED: x should be 10 at upper bound";
