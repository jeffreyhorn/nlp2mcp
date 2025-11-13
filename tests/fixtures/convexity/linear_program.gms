$title Simple Linear Program - Convex Test Fixture

* Expected Classification: CONVEX
* Expected Warning: None (linear programs are always convex)
* Description: Minimizes a linear objective with linear constraints

Variables x, y, obj;

Equations objdef, constr1, constr2;

objdef..  obj =e= 2*x + 3*y;
constr1.. x + y =l= 10;
constr2.. 2*x - y =g= 1;

x.lo = 0;
y.lo = 0;

Model m /all/;
Solve m using nlp minimizing obj;
