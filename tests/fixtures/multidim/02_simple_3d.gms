$onText
Fixture 02: Simple 3D Indexing
Tests: Basic 3D set indexing with y(i,j,k) pattern
$offText

Sets
    i "dimension 1" /i1*i2/
    j "dimension 2" /j1*j2/
    k "dimension 3" /k1*k2/;

Parameters
    c(i,j,k) "3D cost parameter";

Variables
    y(i,j,k) "3D decision variable"
    z "objective variable";

Equations
    obj_def "Objective definition"
    balance(i,j,k) "3D balance constraint";

* Objective: minimize sum of all y variables (nested sums)
obj_def.. z =e= sum(i, sum(j, sum(k, y(i,j,k))));

* 3D constraint: y(i,j,k) <= c(i,j,k)
balance(i,j,k).. y(i,j,k) =l= c(i,j,k);

Model simple_3d /all/;
Solve simple_3d using nlp minimizing z;
