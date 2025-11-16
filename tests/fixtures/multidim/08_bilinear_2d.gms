$onText
Fixture 08: Bilinear Terms with 2D Indexing
Tests: Multi-dimensional bilinear products (regression for convexity detection)
$offText

Sets
    i "set 1" /i1*i2/
    j "set 2" /j1*j2/;

Variables
    x(i,j) "first 2D variable"
    y(i,j) "second 2D variable"
    obj "objective";

Equations
    obj_def "Objective"
    bilinear_eq(i,j) "Bilinear constraint";

* Objective with bilinear term
obj_def.. obj =e= sum(i, sum(j, x(i,j) * y(i,j)));

* Bilinear constraint: x(i,j) * y(i,j) <= 1
bilinear_eq(i,j).. x(i,j) * y(i,j) =l= 1;

Model bilinear_2d /all/;
Solve bilinear_2d using nlp minimizing obj;
