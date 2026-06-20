$title Shape 2 - self-alias Sum (consolidated-alias path)
Set i /i1*i3/;
Alias(i,jj);
Parameter a(i,jj); a(i,jj) = 1;
Parameter d(i); d(i) = 1;
Variable x(i), z;
Equation obj, bal(i);
obj..    z =e= sum(i, x(i));
bal(i).. d(i) =e= sum(jj, a(i,jj)*x(jj));
Model m /all/;
solve m using nlp minimizing z;
