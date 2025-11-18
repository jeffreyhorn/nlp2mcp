$title Variable Attribute Access in Assignments Test
$ontext
Purpose: Test variable .l attribute access (trig.gms pattern)
Pattern: diff1 = 10.0 - x1.l;
Sprint: 8 Day 4
$offtext

Variable x1, x2;
Scalar diff1, diff2;

x1.l = 2.5;
x2.l = 3.7;

diff1 = 10.0 - x1.l;
diff2 = 5.0 - x2.l;

Equation objdef;
objdef.. x1 + x2 =e= 6;

Model m /all/;
solve m using nlp minimizing x1;
