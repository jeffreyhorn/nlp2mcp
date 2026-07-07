$title Shape 9 - objective-gradient subset + fixed-boundary-element consolidation (robert)
* robert (Sprint 30 P1a): a variable s(tt) appears in the objective under TWO
* structurally-different terms — summed over a SUBSET t(tt) with one coefficient,
* and referenced at a FIXED boundary element '4' with another. The indexed
* stationarity consolidation must emit BOTH, each guarded by the condition that
* selects its instances:  sc$(t(tt))  and  rv$(sameas(tt,'4')) — not collapse to a
* single unguarded representative (which drops the subset guard AND the boundary
* term). Same family as #1447 (objective-term subset-scoping), extended to
* fixed-literal-element boundary terms.
Set tt /1*4/;
Set t(tt) /1*3/;
Scalar sc /2/, rv /25/;
Variable s(tt), z;
Positive Variable s;
Equation obj, bnd(tt);
obj..     z =e= sum(t, -sc*s(t)) + rv*s('4');
bnd(tt).. s(tt) =g= 0.1;
Model m /all/;
solve m using nlp maximizing z;
