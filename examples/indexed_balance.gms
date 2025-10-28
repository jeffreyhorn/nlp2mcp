Sets
    i /i1, i2/ ;

Parameters
    demand(i) /i1 3, i2 1/ ;

Variables
    supply(i)
    obj ;

Equations
    objective
    balance(i) ;

objective..
    obj =e= sum(i, supply(i));

balance(i)..
    supply(i) =e= demand(i);

Model indexed_balance / objective, balance / ;
Solve indexed_balance using NLP minimizing obj ;
