* Fixture 5: Option Statement from mhw4dx.gms (Real GAMSLib Example)
* Tests exact pattern from mhw4dx.gms (ensures unlock)
* Simplified excerpt from mhw4dx.gms

Variable m, x1, x2, x3, x4, x5;

x1.l = -1;
x2.l =  2;
x3.l =  1;
x4.l = -2;
x5.l = -2;

option limCol = 0, limRow = 0;

Equation obj;

obj.. m =e= (x1-10)*(x1-10) + 5*(x2-12)*(x2-12) + x3**4
            + 3*(x4-11)*(x4-11) + 10*x5**6;

option decimals = 8;
