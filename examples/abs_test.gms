* Test smooth abs() feature
* Minimize |x - 2|

Variables
    x
    obj ;

Equations
    objective ;

objective..
    obj =e= abs(x - 2);

Model abs_nlp / objective / ;
Solve abs_nlp using NLP minimizing obj ;
