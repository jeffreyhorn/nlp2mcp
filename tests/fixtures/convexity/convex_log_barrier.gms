$title Convex Log Barrier - Convex Test Fixture

* Expected Classification: CONVEX
* Expected Warning: None (-log is convex for positive x when minimizing)
* Description: Minimizes -log(x) - log(y) (log barrier function)

Variables x, y, obj;

Equations objdef, constraint;

objdef..     obj =e= -log(x) - log(y);
constraint.. x + y =l= 10;

x.lo = 0.01;
x.up = 100;
y.lo = 0.01;
y.up = 100;

Model m /all/;
Solve m using nlp minimizing obj;
