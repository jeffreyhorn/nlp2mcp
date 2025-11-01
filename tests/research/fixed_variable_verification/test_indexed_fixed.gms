* Test 2: Indexed variable with .fx for specific indices

Sets
    i /i1, i2, i3/;

Variables
    x(i) "indexed decision variable"
    obj "objective";

* Fix x(i2) to 5.0, leave others free
x.fx("i2") = 5.0;

* Set bounds for i1
x.lo("i1") = 0;
x.up("i1") = 10;

Equations
    objdef "objective definition";

objdef.. obj =e= sum(i, x(i));

Model test /all/;
Solve test using NLP minimizing obj;
