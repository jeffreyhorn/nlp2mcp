$title Non-Convex Bilinear Term - Non-Convex Test Fixture

* Expected Classification: NON-CONVEX
* Expected Warning: Bilinear term x*y in objective (non-convex)
* Description: Product of variables x*y is non-convex

Variables x, y, obj;

Equations objdef, constraint;

objdef..     obj =e= x*y;
constraint.. x + y =l= 10;

x.lo = 0;
x.up = 10;
y.lo = 0;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
