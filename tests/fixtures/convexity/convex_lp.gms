* Convex Linear Program (LP)
*
* This is a simple linear program, which is always convex.
*
* Problem:
*     minimize: 2*x + 3*y
*     subject to:
*         x + y >= 5
*         x >= 0
*         y >= 0
*
* Expected: 0 warnings (all constraints are linear)

Variables
    x
    y
    obj;

Equations
    objective
    constraint1;

* Objective: minimize 2*x + 3*y
objective.. obj =e= 2*x + 3*y;

* Constraint: x + y >= 5
constraint1.. x + y =g= 5;

* Variable bounds
x.lo = 0;
y.lo = 0;

* Model definition and solve
Model linear_program / all /;
Solve linear_program using NLP minimizing obj;
