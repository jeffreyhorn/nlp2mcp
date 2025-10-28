* Minimal NLP input for regression tests
Sets
    i /i1, i2, i3/ ;

Parameters
    a(i) /i1 1, i2 2, i3 3/ ;

Variables
    x(i)
    obj ;

Equations
    objective
    balance(i) ;

objective..
    obj =e= sum(i, a(i) * x(i));

balance(i)..
    x(i) =g= 0 ;

Model sample_nlp / all / ;
Solve sample_nlp using NLP minimizing obj ;
