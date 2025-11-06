* Test Case 1: minimize z where z = min(x, y)
* Expected: Convert to z <= x, z <= y
* Expected solution: z* = 1, x* = 1, y* = 2

Variables x, y, z, obj;

x.lo = 1;
x.up = 10;
y.lo = 2;
y.up = 10;

Equations objdef, minconstraint;

objdef.. obj =e= z;
minconstraint.. z =e= min(x, y);

Model test /all/;
Solve test using NLP minimizing obj;

Display x.l, y.l, z.l, obj.l;
