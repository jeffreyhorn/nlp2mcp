* Partial Parse Fixture 2: Function Call in Assignment Pattern
* Based on circle.gms error pattern
* Expected: Partial parse ~70-100% (function call blocker)

Set i /i1*i10/;
Parameter x(i), y(i);

* These assignments will fail due to uniform() function calls
x(i) = uniform(1,10);
y(i) = uniform(1,10);

Scalar result;
result = sum(i, x(i) + y(i));
display result;
