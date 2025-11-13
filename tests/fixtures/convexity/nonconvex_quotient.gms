$title Non-Convex Quotient - Non-Convex Test Fixture

* Expected Classification: NON-CONVEX
* Expected Warning: Division x/y is generally non-convex
* Description: Quotient of variables

Variables x, y, obj;

Equations objdef, constraint;

objdef..     obj =e= x/y;
constraint.. x + y =g= 2;

x.lo = 0.1;
x.up = 10;
y.lo = 0.1;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
