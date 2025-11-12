* Non-Convex: Circle Constraint (Nonlinear Equality)
*
* This problem contains a nonlinear equality constraint that defines
* a circle. Even though x^2 + y^2 is a convex function, the equality
* constraint x^2 + y^2 = 4 defines a non-convex set (a circle).
*
* Problem:
*     minimize: x + y
*     subject to:
*         x^2 + y^2 = 4  (circle - non-convex!)
*         x >= 0
*         y >= 0
*
* Expected: 1 warning (nonlinear equality constraint)

Variables
    x
    y
    obj;

Equations
    objective
    circle;

* Objective: minimize x + y
objective.. obj =e= x + y;

* Circle constraint: x^2 + y^2 = 4 (NON-CONVEX!)
circle.. x**2 + y**2 =e= 4;

* Variable bounds
x.lo = 0;
y.lo = 0;

* Model definition and solve
Model circle_problem / all /;
Solve circle_problem using NLP minimizing obj;
