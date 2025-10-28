Scalars
    a / 2 / ;

Variables
    x
    obj ;

Equations
    objective
    stationarity ;

objective..
    obj =e= x;

stationarity..
    x + a =e= 0;

Model scalar_nlp / objective, stationarity / ;
Solve scalar_nlp using NLP minimizing obj ;
