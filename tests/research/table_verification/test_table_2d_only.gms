* Test that Table is 2D only
* Multi-dimensional parameters must use Parameter syntax

Sets
    i /i1, i2/
    j /j1, j2/
    k /k1, k2/;

* This should work - 2D table
Table data2d(i,j) "2D table"
       j1  j2
i1     1   2
i2     3   4;

* For 3D data, we would use Parameter syntax instead:
* Parameter data3d(i,j,k) / i1.j1.k1 1, i1.j1.k2 2, ... /;
