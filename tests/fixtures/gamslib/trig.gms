$title Simple Trigonometric Example (TRIG,SEQ=261)

$onText
Simple trigonometric problem from the LGO library

  Solution: x* ~ 2.66695657     f(x*) ~ -3.76250149


Janos Pinter, LGO - Users Guide, Pinter Consulting Services, Halifax,
Canada, 2003.

Keywords: nonlinear programming, mathematics, trigonometric functions
$offText

Variable x1, obj;

Equation objdef, ineq1;

Model m / all /;

objdef.. obj =e= sin(11*x1) + cos(13*x1) - sin(17*x1) - cos(19*x1);

ineq1..  -x1 + 5*sin(x1) =l= 0;

x1.lo = -2;
x1.up =  5;
x1.l  =  1;

solve m using nlp min obj;

Scalar xdiff, fdiff;
xdiff =  2.66695657 - x1.l;
fdiff = -3.76250149 - obj.l;

display xdiff, fdiff;
