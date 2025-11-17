$onText
Fixture 09: Model Declaration with Equation List
Tests: Model declaration specifying specific equations (not /all/)
Priority: High
$offText

Variables
    x, y, z;

Equations
    eq1, eq2, eq3;

eq1.. x + y =e= 5;
eq2.. x - y =e= 1;
eq3.. z =e= x * y;

* Model declaration with specific equation list (not /all/)
Model subset_model /eq1, eq2/;

* Alternative: model with all equations
Model full_model /all/;
