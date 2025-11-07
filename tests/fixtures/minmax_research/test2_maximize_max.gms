* Test Case 2: maximize z where z = max(x, y)
* Expected: Convert to z >= x, z >= y
* Expected solution: z* = 20, y* = 20

Variables x;
Variables y;
Variables z;
Variables obj;

x.up = 10;
y.up = 20;

Equations objdef;
Equations maxconstraint;

objdef.. obj =e= z;
maxconstraint.. z =e= max(x, y);

Model test /all/;
Solve test using NLP maximizing obj;

* Display x.l, y.l, z.l, obj.l;
