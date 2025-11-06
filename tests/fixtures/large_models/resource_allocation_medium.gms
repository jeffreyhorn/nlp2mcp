* Resource Allocation Problem: 50 variables

Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15, i16, i17, i18, i19, i20, i21, i22, i23, i24, i25, i26, i27, i28, i29, i30, i31, i32, i33, i34, i35, i36, i37, i38, i39, i40, i41, i42, i43, i44, i45, i46, i47, i48, i49, i50/
;

Parameters
    a(i) / i1 2, i2 3, i3 4, i4 5, i5 6, i6 7, i7 8, i8 9, i9 10, i10 1, i11 2, i12 3, i13 4, i14 5, i15 6, i16 7, i17 8, i18 9, i19 10, i20 1, i21 2, i22 3, i23 4, i24 5, i25 6, i26 7, i27 8, i28 9, i29 10, i30 1, i31 2, i32 3, i33 4, i34 5, i35 6, i36 7, i37 8, i38 9, i39 10, i40 1, i41 2, i42 3, i43 4, i44 5, i45 6, i46 7, i47 8, i48 9, i49 10, i50 1 /
;

Variables
    x(i) decision variables
    obj objective value
;

Equations
    objdef objective definition
    constraint1 sum constraint
    non_negative(i) nonnegativity constraints
;

objdef.. obj =e= sum(i, a(i)*x(i)*x(i));

constraint1.. sum(i, x(i)) =l= 100;

non_negative(i).. x(i) =g= 0;

Model resource_allocation /all/;
Solve resource_allocation using NLP minimizing obj;
