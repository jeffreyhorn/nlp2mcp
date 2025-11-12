* Convex with Nonlinear Inequality Constraints
*
* This problem has a convex objective and convex inequality constraints.
* Nonlinear inequalities of the form g(x) <= 0 are allowed in convex
* optimization as long as g(x) is convex.
*
* Problem:
*     minimize: x^2 + y^2
*     subject to:
*         x^2 + y^2 <= 25  (convex constraint: inside a circle)
*         x + y >= 5
*         x >= 0
*         y >= 0
*
* Expected: 0 warnings (all inequalities, convex objective and constraints)

Variables
    x
    y
    obj;

Equations
    objective
    constraint1
    constraint2;

* Objective: minimize x^2 + y^2
objective.. obj =e= x**2 + y**2;

* Convex inequality: x^2 + y^2 <= 25
constraint1.. x**2 + y**2 =l= 25;

* Linear inequality: x + y >= 5
constraint2.. x + y =g= 5;

* Variable bounds
x.lo = 0;
y.lo = 0;

* Model definition and solve
Model convex_nlp / all /;
Solve convex_nlp using NLP minimizing obj;
