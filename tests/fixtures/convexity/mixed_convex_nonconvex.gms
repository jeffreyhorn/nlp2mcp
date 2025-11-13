$title Mixed Convex/Non-Convex - Edge Case Test Fixture

* Expected Classification: NON-CONVEX (due to nonlinear equality)
* Expected Warning: Convex objective but nonlinear equality constraint
* Description: Convex objective with non-convex feasible set

Variables x, y, obj;

Equations objdef, nonlinear_eq;

objdef..        obj =e= sqr(x) + sqr(y);
nonlinear_eq..  x*y =e= 1;

x.lo = 0.1;
x.up = 10;
y.lo = 0.1;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
