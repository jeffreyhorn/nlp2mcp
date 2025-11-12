* Non-Convex: Bilinear Terms
*
* This problem contains bilinear terms (products of two variables).
* Bilinear terms x*y are non-convex.
*
* Problem:
*     minimize: x*y  (bilinear objective - non-convex!)
*     subject to:
*         x + y >= 5
*         x >= 1
*         y >= 1
*
* Expected: 1 warning (bilinear term in objective)

Variables
    x
    y
    obj;

Equations
    objective
    constraint1;

* Objective: minimize x*y (BILINEAR - NON-CONVEX!)
objective.. obj =e= x * y;

* Constraint: x + y >= 5
constraint1.. x + y =g= 5;

* Variable bounds
x.lo = 1;
y.lo = 1;

* Model definition and solve
Model bilinear_problem / all /;
Solve bilinear_problem using NLP minimizing obj;
