* Minimal fixture for Sprint 27 #1378: a self-referential in-place parameter
* adjustment (c('i2') = c('i2') * 2) on a parameter that has prior /data/
* values and feeds the NLP objective. Guards that --nlp-presolve does NOT
* double-apply such assignments (the source-model include re-runs them once).
Set i / i1, i2 /;
Parameter c(i) / i1 2.0, i2 3.0 /;
c('i2') = c('i2') * 2;
Variable x(i), z;
x.lo(i) = 0.5;
x.up(i) = 5;
Equation obj, con;
obj.. z =e= sum(i, c(i) * sqr(x(i)));
con.. sum(i, x(i)) =g= 2;
Model m / all /;
solve m using nlp minimizing z;
