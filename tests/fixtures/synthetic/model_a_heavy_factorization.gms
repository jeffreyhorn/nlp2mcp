$Title Model A - Heavy Factorization Opportunities
$Ontext
Synthetic model designed to test heavy factorization simplification.
Expected term reduction: 40-50%

Key patterns:
- Common factor extraction: 2*x + 2*y + 2*z => 2*(x+y+z)
- Variable factorization: x*a + x*b + x*c => x*(a+b+c)
- Nested factorization: 3*x*y + 3*x*z + 6*x*w => 3*x*(y+z+2*w)
$Offtext

Sets
    i /1*3/;

Variables
    x, y, z, w, a, b, c, d, obj;

Equations
    eq1, eq2, eq3, eq4, eq5, eq6, objective_eq;

* Heavy common factor extraction opportunities
eq1.. 2*x + 2*y + 2*z =e= 10;

* Variable factorization
eq2.. x*a + x*b + x*c =e= 5;

* Nested factorization
eq3.. 3*x*y + 3*x*z + 6*x*w =e= 15;

* Multiple factorization opportunities
eq4.. 4*a*x + 4*a*y + 4*b*x + 4*b*y =e= 20;

* Distributed multiplication
eq5.. 5*x*a + 5*x*b + 5*y*a + 5*y*b + 5*z*a + 5*z*b =e= 30;

* Combined common factors with nested terms
eq6.. 2*x*a + 2*x*b + 2*x*c + 2*y*a + 2*y*b + 2*y*c =e= 12;

* Objective with heavy factorization opportunities
objective_eq.. obj =e= 3*x*x + 3*y*y + 3*z*z + 6*x*y + 6*x*z + 6*y*z;

Model model_a /all/;
Solve model_a using nlp minimizing obj;
