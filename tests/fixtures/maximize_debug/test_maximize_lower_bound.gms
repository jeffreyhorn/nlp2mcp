$title Maximize with Lower Bound Only
$ontext
Test: Maximize with lower bound
Purpose: Verify lower bound multiplier behavior
Expected: x should be unbounded above (hit default upper bound)
Bug: This case may not trigger the bug since we're maximizing away from lower bound
KKT condition: Should have stat_x.. ... - piL_x =E= 0 at the bound
$offtext

Variables x, obj;

* Set lower bound - x can't go below 5
x.lo = 5;

Equations objdef;

* Simple linear objective: maximize x
objdef.. obj =e= x;

Model test /all/;

* Solve maximizing - x should go to upper bound (default or infinity)
Solve test using NLP maximizing obj;

Display x.l, obj.l;

* x should be at least 5
abort$(x.l < 5 - 1e-6) "FAILED: x should be >= 5";
