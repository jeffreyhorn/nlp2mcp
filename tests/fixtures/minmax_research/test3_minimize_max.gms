* Test Case 3: minimize z where z = max(x, y)
* Opposite sense combination
* Expected solution: Both x and y should become equal at minimum

Variables x;
Variables y;
Variables z;
Variables obj;

x.lo = 1;
x.up = 10;
y.lo = 2;
y.up = 10;

Equations objdef;
Equations maxconstraint;

objdef.. obj =e= z;
maxconstraint.. z =e= max(x, y);

Model test /all/;
Solve test using NLP minimizing obj;

* Display x.l, y.l, z.l, obj.l;
