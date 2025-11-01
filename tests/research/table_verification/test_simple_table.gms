Sets
    i /i1, i2/
    j /j1, j2/;

Table data(i,j)
       j1  j2
i1     1   2
i2     3   4;

Variables x(i,j), obj;

Equations objdef;

objdef.. obj =e= sum((i,j), data(i,j) * x(i,j));

Model test /all/;
Solve test using NLP minimizing obj;
