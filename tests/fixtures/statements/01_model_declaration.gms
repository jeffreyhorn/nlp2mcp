$onText
Fixture 01: Model Declaration
Tests: Basic model declaration with /all/ syntax
Priority: Critical
$offText

Variables
    x, y;

Equations
    eq1, eq2;

eq1.. x + y =e= 5;
eq2.. x - y =e= 1;

* Model declaration using /all/ (includes all equations)
Model simple /all/;
