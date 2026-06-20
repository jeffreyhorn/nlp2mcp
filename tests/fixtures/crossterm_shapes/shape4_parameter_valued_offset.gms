$title Shape 4 - parameter-valued offset (#1224 mine shape)
Set l /l1*l3/;
Set i /i1*i4/;
Set j /j1*j4/;
Set k /k1*k2/;
Parameter li(k) /k1 1, k2 2/;
Parameter lj(k) /k1 1, k2 1/;
Parameter d(l,i,j); d(l,i,j) = 1;
Variable x(l,i,j), z;
Equation obj, pr(k,l,i,j);
obj..         z =e= sum((l,i,j), x(l,i,j));
pr(k,l,i,j)$(ord(l) < card(l)).. x(l, i+li(k), j+lj(k)) =g= x(l+1,i,j) - d(l,i,j);
Model m /all/;
solve m using nlp minimizing z;
