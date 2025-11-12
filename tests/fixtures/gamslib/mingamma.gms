$title Minimal y of GAMMA(x) (MINGAMMA,SEQ=299)

$onText
Find minimum of y = gamma(x) and y = loggamma(x) for x > 0


Sloane, N J A, The On-Line Encyclopedia of Integer Sequences; Sequence
A030169. https://oeis.org/A030169

Keywords: nonlinear programming, discontinuous derivatives, statistics
$offText

Variable y1, y2, x1, x2;

Equation y1def, y2def;

x1.lo = 0.01;
x2.lo = 0.01;

y1def.. y1 =e= gamma(x1);

y2def.. y2 =e= loggamma(x2);

Model
   m1 / y1def /
   m2 / y2def /;

solve m1 minimizing y1 using nlp;

solve m2 minimizing y2 using nlp;

Scalar
   x1opt   / 1.46163214496836   /
   x1delta
   x2delta
   y1opt   / 0.8856031944108887 /
   y1delta
   y2delta
   y2opt;

y2opt = log(y1opt);

option decimals = 8;

x1delta = x1.l - x1opt;
y1delta = y1.l - y1opt;
x2delta = x2.l - x1opt;
y2delta = y2.l - y2opt;

display x1.l, x2.l, y1.l, y2.l, x1opt, y1opt, y2opt, x1delta, x2delta, y1delta, y2delta;

* A solver can be much more precise on the y value than the x value
* when finding the minimum, so different tolerances are needed.
Scalars
  xtol / 5e-5 /
  ytol / 1e-6 /
  ;
if(m1.solveStat <> %solveStat.capabilityProblems%,
   abort$[abs(x1delta) > xtol or abs(y1delta) > ytol] "inconsistent results with gamma";
);
if(m2.solveStat <> %solveStat.capabilityProblems%,
   abort$[abs(x2delta) > xtol or abs(y2delta) > ytol] "inconsistent results with loggamma";
);
