$onText
Fixture 06: Four-Dimensional Indexing
Tests: 4D set indexing with w(i,j,k,l) pattern
$offText

Sets
    i "dim 1" /i1*i2/
    j "dim 2" /j1*j2/
    k "dim 3" /k1*k2/
    l "dim 4" /l1*l2/;

Variables
    w(i,j,k,l) "4D variable"
    obj "objective";

Equations
    obj_def "Objective"
    constraint_4d(i,j,k,l) "4D constraint";

* Objective: sum over all 4 dimensions (nested sums)
obj_def.. obj =e= sum(i, sum(j, sum(k, sum(l, w(i,j,k,l)))));

* 4D constraint: w(i,j,k,l) <= 10
constraint_4d(i,j,k,l).. w(i,j,k,l) =l= 10;

Model four_dim /all/;
Solve four_dim using nlp minimizing obj;
