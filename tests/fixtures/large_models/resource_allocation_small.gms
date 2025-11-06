* Resource Allocation Problem: 10 variables

Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10/
;

Parameters
    a(i) / i1 2, i2 3, i3 4, i4 5, i5 6, i6 7, i7 8, i8 9, i9 10, i10 1 /
;

Variables
    x(i) decision variables
    obj objective value
;

Equations
    objdef objective definition
    constraint1 sum constraint
    non_negative(i) nonnegativity constraints
;

objdef.. obj =e= sum(i, a(i)*x(i)*x(i));

constraint1.. sum(i, x(i)) =l= 100;

non_negative(i).. x(i) =g= 0;

Model resource_allocation /all/;
Solve resource_allocation using NLP minimizing obj;
