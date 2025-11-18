$title Simple 1D Indexed Assignment Test
$ontext
Purpose: Test basic 1D parameter indexed assignment
Pattern: p('i1') = 10;
Sprint: 8 Day 4
$offtext

Set i /i1, i2, i3/;
Parameter p(i);

p('i1') = 10;
p('i2') = 20;
p('i3') = 30;

display p;
