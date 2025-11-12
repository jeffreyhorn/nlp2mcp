* Non-Convex: Odd Powers
*
* This problem contains odd powers of variables.
* Odd powers (x^3, x^5, etc.) are neither convex nor concave.
*
* Problem:
*     minimize: x**3 + y**3  (odd powers - non-convex!)
*     subject to:
*         x + y >= 5
*         x >= 0
*         y >= 0
*
* Expected: 1 warning (odd powers in objective)

Variables
    x
    y
    obj;

Equations
    objective
    constraint1;

* Objective: minimize x^3 + y^3 (ODD POWERS - NON-CONVEX!)
objective.. obj =e= x**3 + y**3;

* Constraint: x + y >= 5
constraint1.. x + y =g= 5;

* Variable bounds
x.lo = 0;
y.lo = 0;

* Model definition and solve
Model odd_power_problem / all /;
Solve odd_power_problem using NLP minimizing obj;
