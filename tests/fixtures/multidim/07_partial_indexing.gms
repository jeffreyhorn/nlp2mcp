$onText
Fixture 07: Partial Indexing Patterns
Tests: Variables indexed on subset of equation domain
$offText

Sets
    i "set 1" /i1*i3/
    j "set 2" /j1*j2/
    k "set 3" /k1*k2/;

Variables
    x(i) "indexed on i only"
    y(i,j) "indexed on i,j"
    z(i,j,k) "indexed on all dimensions";

Equations
    link_eq(i,j,k) "Equation using all three indices";

* Partial indexing: x(i) is independent of j,k but appears in (i,j,k) equation
link_eq(i,j,k).. z(i,j,k) =e= x(i) + y(i,j);

Model partial_idx /all/;
