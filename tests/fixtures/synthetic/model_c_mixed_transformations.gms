$Title Model C - Mixed Transformation Opportunities
$Ontext
Synthetic model designed to test mixed simplification transformations.
Expected term reduction: 40-60% (actual measured: 51.85%)

Strategy: Mix of factorable and non-factorable expressions
$Offtext

Variables
    x, y, z, w, a, b, c, d, obj;

Equations
    eq1, eq2, eq3, eq4, eq5, objective_eq;

* Moderate factorization: 2*x + 2*y => 2*(x+y)
eq1.. 2*x + 2*y + 3*z =e= 5*w + 7*a;

* No factorization possible - prime coefficients
eq2.. 3*x + 5*y + 7*z =e= 11*w;

* Partial factorization: x*a + x*b => x*(a+b)
eq3.. x*a + x*b + 2*c =e= 3*d;

* No simplification
eq4.. 2*a + 3*b =e= 5*c;

* Moderate factorization
eq5.. 3*x*y + 3*x*z =e= 2*w + 5*a;

* Objective: some factorization possible
objective_eq.. obj =e= 2*x*a + 2*x*b + y + z + w;

Model model_c /all/;
Solve model_c using nlp minimizing obj;
