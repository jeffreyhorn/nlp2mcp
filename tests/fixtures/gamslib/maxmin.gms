$title Max Min Location of Points in Unit Square (MAXMIN,seq=263)

$onText
This test problem locates points in the unit square such that the
distance between any two points is maximized. For certain number
of points we know optimal arrangements. This knowledge is also
used to find a lower bound on the objective by looking for perfect
square arrangements (suggested by S Dirkse).

Several formulations are presented which serve as good examples to
investigate the performance of different solution approaches. The
problem was originally proposed by Dick van Hertog and has been implemented
by Janos Pinter and used extensively by LGO with 13 and 20 points.


E. Stinstra, D. den Hertog, H.P. Stehouwer, A. Vestjens,
Constrained Maximin Designs for Computer Experiments,
Technometrics, 2002. (under revision)

Janos Pinter, LGO - Users Guide, Pinter Consulting Services, Halifax,
Canada, 2003.

Keywords: nonlinear programming, discontinuous derivatives, mathematics,
          maximized minimum distance, circle packing in a square
$offText

$eolCom //
$if not set points $set points 13

Set
   d        'dimension of space' / x, y         /
   n        'number of points'   / p1*p%points% /
   low(n,n) 'lower triangle';

Alias (n,nn);

low(n,nn) = ord(n) > ord(nn);

Variable
   point(n,d) 'coordinates of points'
   dist(n,n)  'distance between all points'
   mindist;

Equation
   defdist(n,n)   'distance definitions'
   mindist1(n,n)  'minimum distance formulation 1'
   mindist1a(n,n) 'minimum distance formulation 1 without dist'
   mindist2       'minimum distance formulation 2'
   mindist2a      'minimum distance formulation 2 without dist';

defdist(low(n,nn))..   dist(low) =e= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));

mindist1(low)..        mindist   =l= dist(low);

mindist1a(low(n,nn)).. mindist   =l= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));

mindist2..  mindist =e= smin(low, dist(low));

mindist2a.. mindist =e= smin(low(n,nn), sqrt(sum(d, sqr(point(n,d) - point(nn,d)))));

Model
   maxmin1  / defdist, mindist1  /
   maxmin2  / defdist, mindist2  /
   maxmin1a /          mindist1a /
   maxmin2a /          mindist2a /;

Scalar p;                     // Pinter's
p = 0;

loop((n,d),                   // original
   p = round(mod(p,10)) + 1;  // nominal
   point.l(n,d) = p/10;       // point  0.1,.2, ... 1.0, 0.1, ...
);

point.lo(n,d)     = 0;
point.up(n,d)     = 1;
point.l (n,d)     = uniform(0,1);
dist.l(low(n,nn)) = sqrt(sqr(point.l(n,'x') - point.l(nn,'x')) + sqr(point.l(n,'y') - point.l(nn,'y')));

point.fx('p1',d) = 0;   // fix one point

Parameter bnd 'lower bound on objective';
bnd = 1/max(ceil(sqrt(card(n)))-1,1);
display bnd;

option limCol = 0, limRow = 0;
if(card(n) > 9, option solPrint = off;);

* for experimentation we will combine different model version
* with different bounds and starting points
*
* dist.lo(low) = -inf;
* dist.lo(low) =  0;
* dist.lo(low) =  0.01;
* dist.lo(low) =  bnd/2;
* dist.lo(low) =  bnd;
*
* solve maxmin1  max mindist using nlp;
* solve maxmin1a max mindist using nlp;
* solve maxmin2  max mindist using dnlp;
* solve maxmin2a max mindist using dnlp;

* maxmin2 and maxmin2a without bounds are well suited for LGO
* maxmin1a with bounds is well suited for conopt3 (bounds 200 point is ok)

solve maxmin1a max mindist using dnlp;

display bnd,mindist.l, point.l;
