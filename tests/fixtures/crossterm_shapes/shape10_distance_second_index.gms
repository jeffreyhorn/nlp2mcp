$title Shape 10 - distance second-index var-at-two-indices cross-term (#1111/#1112 polygon)

* polygon's distance(i,j)$(ord(j)>ord(i))..  sqr(r(i)) + sqr(r(j)) - 2*r(i)*r(j) =l= 1
* The variable r appears at BOTH index positions of the 2-index constraint, so
* stat_r(i) must carry TWO Jacobian-transpose sums, not one:
*   - the first-index sum over j>i with multiplier lam_g(i,j)      (r at position 0)
*   - the complementary second-index sum over j<i with lam_g(j,i)  (r at position 1)
* Before the Sprint-31 P2 fix the second-index sum was dropped (the offset-key
* machinery collapsed both positions into one group and emitted only the position-0
* representative). This guards `_build_complement_index_sum` independently of the
* GAMSlib polygon model.

Set i /i1*i5/;
Alias(i,j);

Variable r(i), tot;
r.lo(i) = 0.1;
r.up(i) = 10;

Equation obj, g(i,j);
obj.. tot =e= sum(i, r(i));
g(i,j)$(ord(j) > ord(i))..  sqr(r(i)) + sqr(r(j)) - 2*r(i)*r(j) =l= 1;

Model m /all/;
solve m maximizing tot using nlp;
