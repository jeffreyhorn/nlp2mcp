$title Circle Enclosing Points - SNOPT Example (CIRCLE,SEQ=201)

$onText
This is an example from the GAMS/SNOPT manual. Find the smallest circle
that contains a number of given points.

https://en.wikipedia.org/wiki/Smallest_circle_problem


Gill, P E, Murray, W, and Saunders, M A, GAMS/SNOPT: An SQP Algorithm
for Large-Scale Constrained Optimization, 1988.

Keywords: nonlinear programming, smallest circle problem, mathematics
$offText

$if not set size $set size 10

Set i 'points' / p1*p%size% /;

Parameter
   x(i) 'x coordinates'
   y(i) 'y coordinates';

* fill with random data
x(i) = uniform(1,10);
y(i) = uniform(1,10);

Variable
   a 'x coordinate of center of circle'
   b 'y coordinate of center of circle'
   r 'radius';

Equation e(i) 'points must be inside circle';

e(i)..  sqr(x(i) - a) + sqr(y(i) - b) =l= sqr(r);

r.lo = 0;

Parameter xmin, ymin, xmax, ymax;
xmin = smin(i, x(i));
ymin = smin(i, y(i));
xmax = smax(i, x(i));
ymax = smax(i, y(i));

* set starting point
a.l = (xmin + xmax)/2;
b.l = (ymin + ymax)/2;
r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));

Model m / all /;

solve m using nlp minimizing r;

if(m.modelStat <> %modelStat.optimal%        and
   m.modelStat <> %modelStat.locallyOptimal% and
   m.modelStat <> %modelStat.feasibleSolution%, abort "stop");
