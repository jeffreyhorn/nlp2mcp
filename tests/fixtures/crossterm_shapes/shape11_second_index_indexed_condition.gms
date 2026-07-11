$title Shape 11 - var-at-two-indices second-index sum with an INDEXED-symbol condition (#1111/#1112)

* Like shape10 (r at both index positions of a 2-index constraint), but the
* constraint's $-condition contains an INDEXED parameter `w(i)` in addition to the
* ord() filter. Building the complementary (second-index) transpose sum swaps the
* two constraint domain names (i<->j) throughout the condition, so `w(i)` must
* become `w(j)`. The swap must pass PLAIN STRING replacements to
* _reindex_condition_symbols — a SymbolRef would be written verbatim into the
* ParamRef index tuple (`w(SymbolRef('j'))`) and later crash _format_mixed_indices.
* This guards that path.

Set i /i1*i5/;
Alias(i,j);
Parameter w(i) /i1 1, i2 1, i3 1, i4 1, i5 1/;

Variable r(i), tot;
r.lo(i) = 0.1;
r.up(i) = 10;

Equation obj, g(i,j);
obj.. tot =e= sum(i, r(i));
g(i,j)$(ord(j) > ord(i) and w(i))..  sqr(r(i)) + sqr(r(j)) - 2*r(i)*r(j) =l= 1;

Model m /all/;
solve m maximizing tot using nlp;
