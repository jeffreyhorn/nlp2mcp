* Resource Allocation Problem: 100 variables

Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15, i16, i17, i18, i19, i20, i21, i22, i23, i24, i25, i26, i27, i28, i29, i30, i31, i32, i33, i34, i35, i36, i37, i38, i39, i40, i41, i42, i43, i44, i45, i46, i47, i48, i49, i50, i51, i52, i53, i54, i55, i56, i57, i58, i59, i60, i61, i62, i63, i64, i65, i66, i67, i68, i69, i70, i71, i72, i73, i74, i75, i76, i77, i78, i79, i80, i81, i82, i83, i84, i85, i86, i87, i88, i89, i90, i91, i92, i93, i94, i95, i96, i97, i98, i99, i100/
;

Parameters
    a(i) / i1 2, i2 3, i3 4, i4 5, i5 6, i6 7, i7 8, i8 9, i9 10, i10 1, i11 2, i12 3, i13 4, i14 5, i15 6, i16 7, i17 8, i18 9, i19 10, i20 1, i21 2, i22 3, i23 4, i24 5, i25 6, i26 7, i27 8, i28 9, i29 10, i30 1, i31 2, i32 3, i33 4, i34 5, i35 6, i36 7, i37 8, i38 9, i39 10, i40 1, i41 2, i42 3, i43 4, i44 5, i45 6, i46 7, i47 8, i48 9, i49 10, i50 1, i51 2, i52 3, i53 4, i54 5, i55 6, i56 7, i57 8, i58 9, i59 10, i60 1, i61 2, i62 3, i63 4, i64 5, i65 6, i66 7, i67 8, i68 9, i69 10, i70 1, i71 2, i72 3, i73 4, i74 5, i75 6, i76 7, i77 8, i78 9, i79 10, i80 1, i81 2, i82 3, i83 4, i84 5, i85 6, i86 7, i87 8, i88 9, i89 10, i90 1, i91 2, i92 3, i93 4, i94 5, i95 6, i96 7, i97 8, i98 9, i99 10, i100 1 /
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
