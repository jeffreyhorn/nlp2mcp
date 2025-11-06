* Test Case 6: Min in constraint (not objective-defining) - should work with standard epigraph
* This is a regression test - min/max in constraints should continue to work
* Expected solution: z* = 1.5

Variables x, y, z, obj;

x.lo = 1;
x.up = 10;
y.lo = 2;
y.up = 10;

Equations objdef, minconstraint;

objdef.. obj =e= z;
minconstraint.. z =g= min(x, y) + 0.5;

Model test /all/;
Solve test using NLP minimizing obj;

Display x.l, y.l, z.l, obj.l;
