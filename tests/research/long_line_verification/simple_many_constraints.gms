Sets
    i / i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15, i16, i17, i18, i19, i20 /;

Parameters
    a(i)
    b(i);

a(i) = 2.0;
b(i) = 10.0;

Variables
    x(i)
    obj;

Equations
    objdef
    con1(i)
    con2(i)
    con3(i)
    con4(i)
    con5(i);

objdef.. obj =e= sum(i, a(i) * x(i));

con1(i).. x(i) =l= b(i);
con2(i).. x(i) =g= 0.5;
con3(i).. x(i) =l= 100;
con4(i).. x(i) =l= 5;
con5(i).. x(i) =l= 50;

x.lo(i) = 0;
x.up(i) = 10;

Model test_model / all /;
solve test_model using nlp minimizing obj;
