Variables
    x
    y
    obj ;

Equations
    objective
    nonlinear ;

objective..
    obj =e= x + y;

nonlinear..
    sin(x) + cos(y) =e= 0;

x.lo = -1;
x.up = 2;
y.lo = 0;
y.up = +INF;

Model bounds_nlp / objective, nonlinear / ;
Solve bounds_nlp using NLP minimizing obj ;
