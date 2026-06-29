$title Shape 8 - successor offset-alias objective cross-term (#1143 polygon)

* polygon's objective sums over the ordinal-successor dynamic subset j(i+1):
*   obj.. tot =e= sum(j(i+1), x(i+1)*x(i))
* so x(i) appears in the sum body at BOTH offset 0 (as x(i)) and offset +1 (as
* x(i+1) in the predecessor row). The per-column objective gradient for an
* INTERIOR x carries both the +1 and -1 offset cross-terms, but a BOUNDARY column
* (x('i1'), whose predecessor row is out of range) carries only the +1 term.
* stat_x(i) must therefore pick an interior representative (#1447/#1143) so the
* predecessor cross-term x(i-1)$(j(i-1)) is NOT dropped for every interior row.

Set i /i1*i5/;
Alias(i,j);

Variable x(i), tot;
x.lo(i) = 0.1;
x.up(i) = 10;

Equation obj;
obj.. tot =e= sum(j(i+1), x(i+1)*x(i));

Model m /all/;
solve m maximizing tot using nlp;
