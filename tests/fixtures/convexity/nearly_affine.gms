$title Nearly Affine - Edge Case Test Fixture

* Expected Classification: NON-CONVEX (technically, due to sqr in equality)
* Expected Warning: Nonlinear equality with sqr(x)
* Description: Almost affine problem but with x^2 = 4 equality

Variables x, y, obj;

Equations objdef, nearly_linear_eq;

objdef..           obj =e= 2*x + 3*y;
nearly_linear_eq.. sqr(x) =e= 4;

x.lo = -5;
x.up = 5;
y.lo = -10;
y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
