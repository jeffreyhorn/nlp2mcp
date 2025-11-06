* Test Case 2: maximize z where z = max(x, y)
* Expected: Convert to z >= x, z >= y (symmetric to test 1)
* Expected solution: z* = 20, x* = 10, y* = 20

Variables x, y, z, obj;

x.lo = 0;
x.up = 10;
y.lo = 0;
y.up = 20;

Equations objdef, maxconstraint;

objdef.. obj =e= z;
maxconstraint.. z =e= max(x, y);

Model test /all/;
Solve test using NLP maximizing obj;

Display x.l, y.l, z.l, obj.l;
