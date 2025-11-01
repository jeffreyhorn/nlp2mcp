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
    constraint1(i)
    constraint2(i)
    constraint3(i)
    constraint4(i)
    constraint5(i);

objdef.. obj =e= sum(i, a(i) * sqr(x(i)));

constraint1(i).. x(i) =l= b(i);
constraint2(i).. x(i) =g= 0;
constraint3(i).. sqr(x(i)) =l= 100;
constraint4(i).. exp(x(i)) =l= 5;
constraint5(i).. x(i) =l= 50;

x.lo(i) = 0;
x.up(i) = 10;

Model test_model / all /;
solve test_model using nlp minimizing obj;
