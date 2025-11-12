$title Hock - Schittkowski 1981 - Problem 62 (HS62,SEQ=264)

$onText
This is a popular test problem from the early 80s. The sqr term
creates problems for some solvers because the second partial
derivatives are not defined. The problems solves much better
if the sqr term is removed.

eq1.. 20*sqr(x1 + x2 + x3 - 1) =e= 0;
eq1..        x1 + x2 + x3 - 1  =e= 0;


Hock and Schittkowski, Lecture Notes in Economics and Mathematical
Systems, Springer Verlag, 1981.

Keywords: nonlinear programming, mathematics, Hock-Schittkowski collection
$offText

Variable obj;

Positive Variable x1, x2, x3;

Equation objdef, eq1, eq1x;

objdef..  obj =e= -32.174*( 255.*log((x1+x2+x3+0.03)/(0.09*x1+x2+x3+0.03))
                          + 280.*log((x2+x3+0.03)/(0.07*x2+x3+0.03))
                          + 290.*log((x3+0.03)/(0.13*x3+0.03)));

eq1 ..    20*sqr(x1 + x2 + x3 - 1) =e= 0;

eq1x..           x1 + x2 + x3 - 1  =e= 0;

Model
   m  / objdef, eq1  /
   mx / objdef, eq1x /;

* x1.l = 1/3; x2.l = 1/3; x3.l = 1/3;

solve m using nlp min obj;
* solve mx using nlp min obj;

Scalar
   global global solution / -0.262725145e5 /
   diff   optcr - relative distance from global;

diff = (global - obj.l)/global;

display global, obj.l, diff;
