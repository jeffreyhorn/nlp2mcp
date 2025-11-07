* Test Case 4: maximize z where z = min(x, y)
* Opposite sense combination
* Expected solution: Both x and y should become equal at maximum

Variables x;
Variables y;
Variables z;
Variables obj;

x.up = 10;
y.up = 20;

Equations objdef;
Equations minconstraint;

objdef.. obj =e= z;
minconstraint.. z =e= min(x, y);

Model test /all/;
Solve test using NLP maximizing obj;

* Display x.l, y.l, z.l, obj.l;
