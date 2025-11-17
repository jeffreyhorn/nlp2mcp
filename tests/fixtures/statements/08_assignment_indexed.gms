$onText
Fixture 08: Indexed Assignment Statement
Tests: Assignment to indexed parameter (currently not supported)
Priority: Medium
Note: This is expected to fail - tests parser error handling
$offText

Sets
    i /i1*i3/;

Parameters
    A(i)
    B(i);

* Indexed assignment - not yet supported by parser
* This fixture tests that parser reports clear error message
A(i) = B(i) + 1;

Variables x;
Equations eq1;

eq1.. x =e= sum(i, A(i));

Model test /all/;
