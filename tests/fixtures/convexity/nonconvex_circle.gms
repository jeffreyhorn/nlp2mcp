$title Non-Convex Circle Equality - Non-Convex Test Fixture

* Expected Classification: NON-CONVEX
* Expected Warning: Nonlinear equality constraint (x^2 + y^2 = 4)
* Description: Circle constraint as equality is non-convex

Variables x, y, obj;

Equations objdef, circle_eq;

objdef..    obj =e= x + y;
circle_eq.. sqr(x) + sqr(y) =e= 4;

x.lo = -3;
x.up = 3;
y.lo = -3;
y.up = 3;

Model m /all/;
Solve m using nlp minimizing obj;
