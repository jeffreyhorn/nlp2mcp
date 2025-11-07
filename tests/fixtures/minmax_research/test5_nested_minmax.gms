* Test Case 5: Nested min/max - minimize z where z = max(min(x,y), w)
* Expected solution: z* = 1.5 (max of min(1,2)=1 and w=1.5)

Variables x;
Variables y;
Variables w;
Variables z;
Variables obj;

x.lo = 1;
x.up = 10;
y.lo = 2;
y.up = 10;
w.lo = 1.5;
w.up = 5;

Equations objdef;
Equations nestedconstraint;

objdef.. obj =e= z;
nestedconstraint.. z =e= max(min(x, y), w);

Model test /all/;
Solve test using NLP minimizing obj;

* Display x.l, y.l, w.l, z.l, obj.l;
