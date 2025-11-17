$onText
Fixture 02: Basic Solve Statement
Tests: solve statement with nlp solver
Priority: Critical
$offText

Variables
    x, y, obj;

Equations
    obj_def, constraint;

obj_def.. obj =e= x * x + y * y;
constraint.. x + y =e= 1;

Model mymodel /all/;
Solve mymodel using nlp minimizing obj;
