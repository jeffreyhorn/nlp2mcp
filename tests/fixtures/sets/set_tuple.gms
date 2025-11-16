* set_tuple.gms - Set tuple notation test
* Tests: Set ij(i,j) with tuple notation

Sets
    i / i1*i3 /
    j / j1*j2 /
    ij(i,j) / i1.j1, i2.j1, i3.j2 /;

Parameters
    A(i,j);

A(ij) = 1;

Scalars
    sum;

sum = sum((i,j), A(i,j));

display sum;
