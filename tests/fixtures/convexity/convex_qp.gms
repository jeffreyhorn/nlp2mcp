$title Convex Quadratic Program - Convex Test Fixture

* Expected Classification: CONVEX
* Expected Warning: None (positive definite quadratic is convex)
* Description: Minimizes x^2 + y^2 (Euclidean norm squared)

Variables x, y, obj;

Equations objdef, linear_constr;

objdef..        obj =e= sqr(x) + sqr(y);
linear_constr.. x + 2*y =l= 5;

x.lo = -10;
x.up = 10;
y.lo = -10;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
