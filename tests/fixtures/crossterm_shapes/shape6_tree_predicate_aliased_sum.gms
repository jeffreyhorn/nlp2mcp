$title Shape 6 - tree-predicate-conditioned aliased Sum (#1390 kand shape)
Set n /n1*n4/;
Alias(n,nn);
Set tree(n,nn);
tree(n,nn) = yes$(ord(nn) = ord(n) + 1);
Parameter d(n); d(n) = 1;
Variable y(n), z;
Equation obj, dembal(n);
obj..       z =e= sum(n, y(n));
dembal(n).. d(n) =e= sum(nn$tree(nn,n), y(nn));
Model m /all/;
solve m using nlp minimizing z;
