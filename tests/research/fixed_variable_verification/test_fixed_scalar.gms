* Test 1: Simple scalar variable with .fx

Variables
    x "decision variable"
    y "free variable"
    obj "objective";

* Fix x to 10.0
x.fx = 10.0;

* y is free
y.lo = -INF;
y.up = INF;

Equations
    objdef "objective definition";

objdef.. obj =e= x + y;

Model test /all/;
Solve test using NLP minimizing obj;
