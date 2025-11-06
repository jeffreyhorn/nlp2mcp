* Test Case 4: maximize z where z = min(x, y) (opposite sense)
* Question: Does z <= x, z <= y work when maximizing?
* Expected solution: z* = 10 (the maximum value that satisfies both constraints)

Variables x, y, z, obj;

x.lo = 0;
x.up = 10;
y.lo = 0;
y.up = 15;

Equations objdef, minconstraint;

objdef.. obj =e= z;
minconstraint.. z =e= min(x, y);

Model test /all/;
Solve test using NLP maximizing obj;

Display x.l, y.l, z.l, obj.l;
