$onText
Fixture 03: Solve with Objective Variable
Tests: solve statement with explicit objective variable
Priority: High
$offText

Sets
    i /i1*i3/;

Variables
    x(i)
    z;

Equations
    obj_def, bounds(i);

obj_def.. z =e= sum(i, x(i) * x(i));
bounds(i).. x(i) =g= 0;

Model opt /all/;
Solve opt using nlp minimizing z;
