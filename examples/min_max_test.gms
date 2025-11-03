* Simple min/max test case
* Minimize z where z = min(x, y)

Variables
    x
    y
    z
    obj ;

Equations
    objective
    min_constraint ;

objective..
    obj =e= z;

min_constraint..
    z =e= min(x, y);

x.lo = 1;
y.lo = 2;

Model min_max_nlp / objective, min_constraint / ;
Solve min_max_nlp using NLP minimizing obj ;
