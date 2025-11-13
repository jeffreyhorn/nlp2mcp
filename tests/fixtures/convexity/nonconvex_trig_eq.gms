$title Non-Convex Trigonometric Equality - Non-Convex Test Fixture

* Expected Classification: NON-CONVEX
* Expected Warning: Trigonometric functions in equality constraint
* Description: sin(x) + cos(y) = 0 is nonlinear equality

Variables x, y, obj;

Equations objdef, trig_eq;

objdef..  obj =e= sqr(x) + sqr(y);
trig_eq.. sin(x) + cos(y) =e= 0;

x.lo = -10;
x.up = 10;
y.lo = -10;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
