$onText
Fixture 05: Display Statement
Tests: display statement (parser should skip/ignore)
Priority: Medium
$offText

Variables
    x, y;

Parameters
    p1, p2;

* Display statements show values during execution
* Parser should recognize and skip these (not fail)
display x.l, y.l;
display p1, p2;

Equations eq1;
eq1.. x + y =e= 1;

Model test /all/;
