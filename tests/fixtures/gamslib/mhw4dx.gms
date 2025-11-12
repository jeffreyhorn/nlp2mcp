$title Nonlinear Test Problem (MHW4DX,SEQ=267)

$onText
This popular test problem has several local solutions, local minima
with obj value of 27.87190522, 44.02207169, and 52.90257967, and the
global minimum with an obj value of 0.02931083. Additional programming
is done to test that we are close to one of these solutions.


Wright, M H, Numerical Methods for Nonlinearly Constraint Optimization.
PhD thesis, Stanford University, 1976.

Keywords: nonlinear programming, mathematics, global optimization, constraint
          optimization
$offText

Variable m, x1, x2, x3, x4, x5;

Equation funct, eq1, eq2, eq3;

funct.. m =e= sqr(x1-1) + sqr(x1-x2) + power(x2-x3,3) + power(x3-x4,4) + power(x4-x5,4);

eq1..   x1 + sqr(x2) + power(x3,3) =e= 3*sqrt(2) + 2;

eq2..   x2 - sqr(x3) + x4          =e= 2*sqrt(2) - 2;

eq3..   x1*x5 =e= 2;

Model wright / all /;

x1.l = -1;
x2.l =  2;
x3.l =  1;
x4.l = -2;
x5.l = -2;

option limCol = 0, limRow = 0;

solve wright using nlp minimizing m;

* there are at least four solutions:
* 52.90257967
* 44.02207169
* 27.87190522
*  0.02931083 global

option decimals = 8;

display m.l, x1.l, x2.l, x3.l, x4.l, x5.l;

$eolCom //

Scalar tol / 1e-2 /;

if(       abs(m.l-52.90257967) < tol, // local solution
   abort$(abs(x1.L-.728003827) > tol) 'x1.l is bad';
   abort$(abs(x2.L+2.24521084) > tol) 'x2.l is bad';
   abort$(abs(x3.L-.779513778) > tol) 'x3.l is bad';
   abort$(abs(x4.L-3.68127970) > tol) 'x4.l is bad';
   abort$(abs(x5.L-2.74723830) > tol) 'x5.l is bad';
   display 'good local solution';
   abort$(wright.modelStat = %modelStat.optimal%) 'solver report a local solution as global';
elseif    abs(m.l-44.02207169) < tol, // local solution
   abort$(abs(x1.L+0.70339279) > tol) 'x1.l is bad';
   abort$(abs(x2.L-2.63570261) > tol) 'x2.l is bad';
   abort$(abs(x3.L+0.09636181) > tol) 'x3.l is bad';
   abort$(abs(x4.L+1.79798989) > tol) 'x4.l is bad';
   abort$(abs(x5.L+2.84336154) > tol) 'x5.l is bad';
   display 'good local solution';
   abort$(wright.modelStat = %modelStat.optimal%) 'solver report a local solution as global';
elseif    abs(m.l-27.87190522) < tol, // local solution
   abort$(abs(x1.L+1.27305303) > tol) 'x1.l is bad';
   abort$(abs(x2.L-2.41035427) > tol) 'x2.l is bad';
   abort$(abs(x3.L-1.19485902) > tol) 'x3.l is bad';
   abort$(abs(x4.L+0.15423906) > tol) 'x4.l is bad';
   abort$(abs(x5.L+1.57102647) > tol) 'x5.l is bad';
   display 'good local solution';
   abort$(wright.modelStat = %modelStat.optimal%) 'solver report a local solution as global';
elseif    abs(m.L -0.02931083) < tol,
   abort$(abs(x1.L-1.11663475) > tol) 'x1.l is bad';
   abort$(abs(x2.L-1.22044082) > tol) 'x2.l is bad';
   abort$(abs(x3.L-1.53778539) > tol) 'x3.l is bad';
   abort$(abs(x4.L-1.97277020) > tol) 'x4.l is bad';
   abort$(abs(x5.L-1.79109597) > tol) 'x5.l is bad';
   display 'this is the global solution';
else
   abort$yes 'unknown solution';
);
