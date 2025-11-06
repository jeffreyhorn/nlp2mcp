* Test Case 3: minimize z where z = max(x, y) (opposite sense)
* Question: Does z >= x, z >= y work when minimizing?
* Expected solution: z* = 2 (the minimum value that satisfies both constraints)

Variables x, y, z, obj;

x.lo = 1;
x.up = 10;
y.lo = 2;
y.up = 10;

Equations objdef, maxconstraint;

objdef.. obj =e= z;
maxconstraint.. z =e= max(x, y);

Model test using NLP minimizing obj;
Solve test;

Display x.l, y.l, z.l, obj.l;
