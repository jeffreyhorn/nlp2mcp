* Convex Quadratic Program (QP)
*
* This is a convex quadratic program with a positive semi-definite
* quadratic objective.
*
* Problem:
*     minimize: x^2 + y^2
*     subject to:
*         x + y >= 5
*         x >= 0
*         y >= 0
*
* Expected: 0 warnings (objective is convex quadratic, constraints are linear)

Variables
    x
    y
    obj;

Equations
    objective
    constraint1;

* Objective: minimize x^2 + y^2 (convex quadratic)
objective.. obj =e= x**2 + y**2;

* Constraint: x + y >= 5
constraint1.. x + y =g= 5;

* Variable bounds
x.lo = 0;
y.lo = 0;

* Model definition and solve
Model quadratic_program / all /;
Solve quadratic_program using NLP minimizing obj;
