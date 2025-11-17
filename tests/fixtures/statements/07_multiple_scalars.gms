$onText
Fixture 07: Multiple Scalar Declarations
Tests: Multiple scalars in single statement
Priority: Critical
$offText

* Multiple scalars declared in comma-separated list
Scalars
    alpha /0.5/
    beta /1.5/
    gamma /2.0/;

* Additional scalars without initial values
Scalars delta, epsilon;

Variables x;
Equations eq1;

eq1.. x =e= alpha + beta + gamma;

Model test /all/;
