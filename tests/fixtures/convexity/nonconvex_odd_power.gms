$title Non-Convex Odd Power - Non-Convex Test Fixture

* Expected Classification: NON-CONVEX
* Expected Warning: Cubic term x^3 is non-convex (neither convex nor concave)
* Description: Odd power terms are non-convex

Variables x, y, obj;

Equations objdef, constraint;

objdef..     obj =e= power(x, 3) + sqr(y);
constraint.. x + y =l= 5;

x.lo = -10;
x.up = 10;
y.lo = -10;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
