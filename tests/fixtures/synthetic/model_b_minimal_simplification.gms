$Title Model B - Minimal Simplification Opportunities
$Ontext
Synthetic model designed to test baseline simplification behavior.
Expected term reduction: ~60% (actual measured: 59.09%)

Strategy: Use already-simplified expressions with no common factors
$Offtext

Variables
    x, y, z, w, a, b, c, obj;

Equations
    eq1, eq2, eq3, objective_eq;

* Already simplified - no common factors (prime coefficients)
eq1.. 3*x + 5*y + 7*z + 11*w =e= 2*a + 13*b + 17*c;

* Simple linear combination - distinct coefficients
eq2.. 2*x + 3*y =e= 5*z + 7*w;

* Pre-factored form - no further simplification
eq3.. 2*(x + y) =e= 3*(z + w);

* Objective: simple sum
objective_eq.. obj =e= x + y + z + w + a + b + c;

Model model_b /all/;
Solve model_b using nlp minimizing obj;
