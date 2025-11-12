* Non-Convex: Trigonometric Functions
*
* This problem contains trigonometric functions in an equality constraint.
* Trig functions are neither convex nor concave, and the equality makes
* the feasible set non-convex.
*
* Problem:
*     minimize: x + y
*     subject to:
*         sin(x) + cos(y) = 0  (trig + nonlinear equality - non-convex!)
*         x >= 0
*         y >= 0
*
* Expected: 2 warnings (trigonometric function + nonlinear equality)

Variables
    x
    y
    obj;

Equations
    objective
    trig_constraint;

* Objective: minimize x + y
objective.. obj =e= x + y;

* Trig constraint: sin(x) + cos(y) = 0 (NON-CONVEX!)
trig_constraint.. sin(x) + cos(y) =e= 0;

* Variable bounds
x.lo = 0;
y.lo = 0;
x.up = 10;
y.up = 10;

* Model definition and solve
Model trig_problem / all /;
Solve trig_problem using NLP minimizing obj;
