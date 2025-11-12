$title Convex with Convex Inequality - Convex Test Fixture

* Expected Classification: CONVEX
* Expected Warning: None (convex objective with convex inequality constraints)
* Description: Convex objective with sqr(x) + sqr(y) <= 25

Variables x, y, obj;

Equations objdef, convex_constr;

objdef..       obj =e= x + 2*y;
convex_constr.. sqr(x) + sqr(y) =l= 25;

x.lo = -10;
x.up = 10;
y.lo = -10;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
