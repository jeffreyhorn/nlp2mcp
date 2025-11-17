$onText
Fixture 06: Scalar Assignment
Tests: Scalar declaration with assignment
Priority: High
$offText

* Scalars with initial values
Scalar pi /3.14159/;
Scalar e /2.71828/;
Scalar tolerance /1e-6/;

Variables x;
Equations eq1;

eq1.. x =e= pi + e;

Model test /all/;
