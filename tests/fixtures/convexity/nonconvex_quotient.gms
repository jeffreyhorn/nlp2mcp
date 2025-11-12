* Non-Convex: Variable Quotients
*
* This problem contains a quotient with a variable in the denominator.
* Quotients x/y where y is a variable are typically non-convex.
*
* Problem:
*     minimize: x/y  (variable quotient - non-convex!)
*     subject to:
*         x + y >= 5
*         x >= 1
*         y >= 1
*
* Expected: 1 warning (variable quotient in objective)

Variables
    x
    y
    obj;

Equations
    objective
    constraint1;

* Objective: minimize x/y (QUOTIENT - NON-CONVEX!)
objective.. obj =e= x / y;

* Constraint: x + y >= 5
constraint1.. x + y =g= 5;

* Variable bounds
x.lo = 1;
y.lo = 1;

* Model definition and solve
Model quotient_problem / all /;
Solve quotient_problem using NLP minimizing obj;
