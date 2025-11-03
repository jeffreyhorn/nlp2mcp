Variables
    x
    y
    obj ;

Equations
    objective
    trig_balance
    poly_balance ;

objective..
    obj =e= x + y;

trig_balance..
    sin(x) + cos(y) =e= 0;

poly_balance..
    x ** 2 + y ** 2 =e= 4;

x.lo = -2;
x.up = 2;
y.lo = -2;
y.up = 2;

* Provide good initial values
x.l = 1.5;
y.l = 1.3;

Model nonlinear_mix / objective, trig_balance, poly_balance / ;
Solve nonlinear_mix using NLP minimizing obj ;
