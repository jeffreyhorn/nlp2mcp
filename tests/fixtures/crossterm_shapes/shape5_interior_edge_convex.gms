$title Shape 5 - interior+edge convex-combination (#1388 camshape shape)
Set i /i1*i5/;
Set first(i); first(i) = yes$(ord(i) = 1);
Set last(i);  last(i)  = yes$(ord(i) = card(i));
Set middle(i); middle(i) = yes$(ord(i) > 1 and ord(i) < card(i));
Scalar cth /0.5/, rmin /1/, rmax /5/;
Variable r(i), z;
Equation obj, convexity(i), convex_edge1(i), convex_edge3(i);
obj..            z =e= sum(i, r(i));
convexity(middle(i)).. (-r(i-1))*r(i) - r(i)*r(i+1) + 2*r(i-1)*r(i+1)*cth =l= 0;
convex_edge1(first(i)).. (-rmin)*r(i) - r(i)*r(i+1) + 2*rmin*r(i+1)*cth =l= 0;
convex_edge3(last(i)).. (-r(i-1))*r(i) - r(i)*rmax + 2*r(i-1)*rmax*cth =l= 0;
Model m /all/;
solve m using nlp minimizing z;
