$title Shape 3 - cross-set alias Sum (Pattern-C gate over-reach guard)
Set i /i1*i3/;
Set j /j1*j2/;
Parameter b(i,j); b(i,j) = 1;
Parameter d(i); d(i) = 1;
Variable x(j), z;
Equation obj, dem(i);
obj..    z =e= sum(j, x(j));
dem(i).. d(i) =g= sum(j, b(i,j)*x(j));
Model m /all/;
solve m using nlp minimizing z;
