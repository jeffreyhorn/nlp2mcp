* Partial Parse Fixture 1: Lead/Lag Indexing Pattern
* Based on himmel16.gms error pattern
* Expected: Partial parse ~80-92% (i++1 blocker)

Set i /i1*i5/;
Variable x(i), y(i), area(i);
Equation areadef(i);

* This equation will fail due to i++1 indexing
areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));

Model m /all/;
solve m using nlp minimizing area('i1');
