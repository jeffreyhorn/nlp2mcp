* Resource Allocation Problem: 250 variables

Sets
    i /i1*i250/
;

Parameters
    a(i) / i1 2, i2 3, i3 4, i4 5, i5 6, i6 7, i7 8, i8 9, i9 10, i10 1, i11 2, i12 3, i13 4, i14 5, i15 6, i16 7, i17 8, i18 9, i19 10, i20 1, i21 2, i22 3, i23 4, i24 5, i25 6, i26 7, i27 8, i28 9, i29 10, i30 1, i31 2, i32 3, i33 4, i34 5, i35 6, i36 7, i37 8, i38 9, i39 10, i40 1, i41 2, i42 3, i43 4, i44 5, i45 6, i46 7, i47 8, i48 9, i49 10, i50 1, i51 2, i52 3, i53 4, i54 5, i55 6, i56 7, i57 8, i58 9, i59 10, i60 1, i61 2, i62 3, i63 4, i64 5, i65 6, i66 7, i67 8, i68 9, i69 10, i70 1, i71 2, i72 3, i73 4, i74 5, i75 6, i76 7, i77 8, i78 9, i79 10, i80 1, i81 2, i82 3, i83 4, i84 5, i85 6, i86 7, i87 8, i88 9, i89 10, i90 1, i91 2, i92 3, i93 4, i94 5, i95 6, i96 7, i97 8, i98 9, i99 10, i100 1, i101 2, i102 3, i103 4, i104 5, i105 6, i106 7, i107 8, i108 9, i109 10, i110 1, i111 2, i112 3, i113 4, i114 5, i115 6, i116 7, i117 8, i118 9, i119 10, i120 1, i121 2, i122 3, i123 4, i124 5, i125 6, i126 7, i127 8, i128 9, i129 10, i130 1, i131 2, i132 3, i133 4, i134 5, i135 6, i136 7, i137 8, i138 9, i139 10, i140 1, i141 2, i142 3, i143 4, i144 5, i145 6, i146 7, i147 8, i148 9, i149 10, i150 1, i151 2, i152 3, i153 4, i154 5, i155 6, i156 7, i157 8, i158 9, i159 10, i160 1, i161 2, i162 3, i163 4, i164 5, i165 6, i166 7, i167 8, i168 9, i169 10, i170 1, i171 2, i172 3, i173 4, i174 5, i175 6, i176 7, i177 8, i178 9, i179 10, i180 1, i181 2, i182 3, i183 4, i184 5, i185 6, i186 7, i187 8, i188 9, i189 10, i190 1, i191 2, i192 3, i193 4, i194 5, i195 6, i196 7, i197 8, i198 9, i199 10, i200 1, i201 2, i202 3, i203 4, i204 5, i205 6, i206 7, i207 8, i208 9, i209 10, i210 1, i211 2, i212 3, i213 4, i214 5, i215 6, i216 7, i217 8, i218 9, i219 10, i220 1, i221 2, i222 3, i223 4, i224 5, i225 6, i226 7, i227 8, i228 9, i229 10, i230 1, i231 2, i232 3, i233 4, i234 5, i235 6, i236 7, i237 8, i238 9, i239 10, i240 1, i241 2, i242 3, i243 4, i244 5, i245 6, i246 7, i247 8, i248 9, i249 10, i250 1 /
;

Variables
    x(i)
    obj
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
