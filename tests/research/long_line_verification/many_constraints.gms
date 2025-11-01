Variables x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19, x20, obj;

Equations objdef, con1, con2, con3, con4, con5, con6, con7, con8, con9, con10, con11, con12, con13, con14, con15, con16, con17, con18, con19, con20;

objdef.. obj =e= x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 + x10 + x11 + x12 + x13 + x14 + x15 + x16 + x17 + x18 + x19 + x20;

con1.. x1 + x2 =l= 10;
con2.. x2 + x3 =l= 10;
con3.. x3 + x4 =l= 10;
con4.. x4 + x5 =l= 10;
con5.. x5 + x6 =l= 10;
con6.. x6 + x7 =l= 10;
con7.. x7 + x8 =l= 10;
con8.. x8 + x9 =l= 10;
con9.. x9 + x10 =l= 10;
con10.. x10 + x11 =l= 10;
con11.. x11 + x12 =l= 10;
con12.. x12 + x13 =l= 10;
con13.. x13 + x14 =l= 10;
con14.. x14 + x15 =l= 10;
con15.. x15 + x16 =l= 10;
con16.. x16 + x17 =l= 10;
con17.. x17 + x18 =l= 10;
con18.. x18 + x19 =l= 10;
con19.. x19 + x20 =l= 10;
con20.. x1 + x20 =l= 10;

x1.lo = 0; x1.up = 10;
x2.lo = 0; x2.up = 10;
x3.lo = 0; x3.up = 10;
x4.lo = 0; x4.up = 10;
x5.lo = 0; x5.up = 10;
x6.lo = 0; x6.up = 10;
x7.lo = 0; x7.up = 10;
x8.lo = 0; x8.up = 10;
x9.lo = 0; x9.up = 10;
x10.lo = 0; x10.up = 10;
x11.lo = 0; x11.up = 10;
x12.lo = 0; x12.up = 10;
x13.lo = 0; x13.up = 10;
x14.lo = 0; x14.up = 10;
x15.lo = 0; x15.up = 10;
x16.lo = 0; x16.up = 10;
x17.lo = 0; x17.up = 10;
x18.lo = 0; x18.up = 10;
x19.lo = 0; x19.up = 10;
x20.lo = 0; x20.up = 10;

Model test_model / all /;
solve test_model using nlp minimizing obj;
