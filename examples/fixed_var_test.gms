* Test fixed variable feature
* Minimize x^2 + y^2 with y fixed at 3

Variables
    x
    y
    obj ;

Equations
    objective ;

objective..
    obj =e= x + y;

y.fx = 3;

Model fixed_nlp / objective / ;
Solve fixed_nlp using NLP minimizing obj ;
