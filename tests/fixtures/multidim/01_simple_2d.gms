$onText
Fixture 01: Simple 2D Indexing
Tests: Basic 2D set indexing with x(i,j) pattern
$offText

Sets
    i "rows" /i1*i3/
    j "columns" /j1*j2/;

Parameters
    a(i,j) "2D parameter";

Variables
    x(i,j) "2D decision variable";

Equations
    simple_eq(i,j) "Simple 2D constraint";

* Simple 2D equation: x(i,j) = a(i,j)
simple_eq(i,j).. x(i,j) =e= a(i,j);

Model simple_2d /all/;
