$title Convex with Trig Inequality - Edge Case Test Fixture

* Expected Classification: AMBIGUOUS (depends on heuristic strictness)
* Expected Warning: May warn about trig functions (conservative approach)
* Description: Linear objective with sin(x) <= 0.5 (may or may not be convex)

Variables x, y, obj;

Equations objdef, trig_ineq;

objdef..    obj =e= x + y;
trig_ineq.. sin(x) =l= 0.5;

x.lo = -10;
x.up = 10;
y.lo = -10;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
