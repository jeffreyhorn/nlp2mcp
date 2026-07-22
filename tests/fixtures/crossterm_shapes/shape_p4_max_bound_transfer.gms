$title P4 - MAXIMIZE bound-transfer sign (sense-aware abs(var.m); Sprint 34 Day 4)
* A MAXIMIZE NLP with an active lower bound on x. The --nlp-presolve warm-start
* must transfer the bound multiplier as `piL_x.l$(...) = abs(x.m)` WITHOUT the
* min-convention sign gate (`and x.m > 0`) — a MAXIMIZE reduced cost is |x.m|,
* so the min-convention gate would skip the correctly-signed multiplier and
* leave piL at 0 (a wrong warm start). Guards the Day-4 (P4) Option-B fix.
Variable z;
Positive Variable x;
x.lo = 1;
Equation obj, cap;
obj.. z =e= 3*x - sqr(x);
cap.. x =l= 10;
Model m /all/;
solve m using nlp maximizing z;
