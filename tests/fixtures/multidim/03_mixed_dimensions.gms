$onText
Fixture 03: Mixed Dimensional Structures
Tests: Combination of 1D, 2D, and 3D variables in same model
$offText

Sets
    i "set 1" /i1*i2/
    j "set 2" /j1*j2/
    k "set 3" /k1*k2/;

Variables
    x(i) "1D variable"
    y(i,j) "2D variable"
    z(i,j,k) "3D variable";

Equations
    link_1d_2d(i,j) "Link 1D and 2D"
    link_2d_3d(i,j,k) "Link 2D and 3D";

* Link equations between different dimensions
link_1d_2d(i,j).. y(i,j) =g= x(i);
link_2d_3d(i,j,k).. z(i,j,k) =g= y(i,j);

Model mixed_dims /all/;
