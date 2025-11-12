$title Maximize Simple Test - No Bounds
$ontext
Test: Maximize without bounds
Purpose: Baseline test to verify maximize works when no bound multipliers are involved
Expected: x should be unbounded (or hit default bounds)
Bug symptom: Should not show bug since no explicit bounds
$offtext

Variables x, obj;

Equations objdef;

* Simple linear objective: maximize x
objdef.. obj =e= x;

Model test /all/;

* Solve maximizing
Solve test using NLP maximizing obj;

Display x.l, obj.l;
