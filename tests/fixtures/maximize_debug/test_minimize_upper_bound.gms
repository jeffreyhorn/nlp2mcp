$title Minimize with Upper Bound (Control Test)
$ontext
Test: Minimize with upper bound - CONTROL TEST
Purpose: Verify minimize still works correctly (should already work)
Expected solution: x = -INF or default lower bound (minimize pushes x down)
This test confirms the current implementation works for minimize
$offtext

Variables x, obj;

* Set upper bound
x.up = 10;

Equations objdef;

* Simple linear objective: minimize x
objdef.. obj =e= x;

Model test /all/;

* Solve minimizing - should push x down
Solve test using NLP minimizing obj;

Display x.l, obj.l;

* x should be well below upper bound
abort$(x.l > 9) "FAILED: x should be far below upper bound for minimize";
