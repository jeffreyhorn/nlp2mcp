$title Convex Exponential - Convex Test Fixture

* Expected Classification: CONVEX
* Expected Warning: None (exp is convex when minimizing)
* Description: Minimizes exp(x) + exp(y)

Variables x, y, obj;

Equations objdef, constraint;

objdef..     obj =e= exp(x) + exp(y);
constraint.. x + y =g= 2;

x.lo = 0;
x.up = 10;
y.lo = 0;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
