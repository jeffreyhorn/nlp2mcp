* Ill-Conditioned System with Scaling Example
* Demonstrates: Curtis-Reid scaling for poorly scaled problems
* Sprint 4 Feature: --scale auto|byvar for improved conditioning
* Note: Compare results with and without --scale flag

Sets
    i Variables /x1*x3/
;

Parameters
    * Deliberately ill-conditioned coefficients
    * Large magnitude differences create numerical issues
    largeCoeff /1e6/
    smallCoeff /1e-6/
;

Variables
    x(i) Decision variables
    obj Objective value
;

Equations
    objective Define objective
    constraint1 First constraint (large coefficients)
    constraint2 Second constraint (small coefficients)
    constraint3 Mixed coefficients
;

* Poorly scaled objective: huge difference in variable importance
objective..
    obj =E= largeCoeff * sqr(x('x1'))
          + x('x2')
          + smallCoeff * sqr(x('x3'));

* Constraint with large coefficients
constraint1..
    largeCoeff * x('x1') + x('x2') =E= largeCoeff * 2;

* Constraint with small coefficients
constraint2..
    smallCoeff * x('x2') + x('x3') =E= smallCoeff * 5;

* Mixed scale constraint
constraint3..
    x('x1') + largeCoeff * x('x2') + smallCoeff * x('x3') =G= 1;

* Initial values
x.l(i) = 1.0;

* Variable bounds
x.lo(i) = 0;
x.up(i) = 10;

Model illconditioned /all/;
Solve illconditioned using NLP minimizing obj;

Display x.l, obj.l;

* Usage:
* Without scaling: nlp2mcp sprint4_scaling_illconditioned.gms -o output.gms
* With auto scaling: nlp2mcp sprint4_scaling_illconditioned.gms -o output.gms --scale auto
* With byvar scaling: nlp2mcp sprint4_scaling_illconditioned.gms -o output.gms --scale byvar
*
* Expected behavior:
* - Without scaling: may have numerical issues
* - With --scale auto: Curtis-Reid scaling improves conditioning
* - With --scale byvar: Per-variable scaling improves conditioning
*
* Check diagnostics with: --stats --dump-jacobian jac.mtx
