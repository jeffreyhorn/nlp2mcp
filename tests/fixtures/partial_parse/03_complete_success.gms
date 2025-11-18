* Partial Parse Fixture 3: Complete Success Baseline
* Expected: 100% parse success (baseline for partial metrics)

Set i /1*5/;
Parameter p(i) /1 10, 2 20, 3 30/;
Scalar x /5/;

Variable obj;
Equation objdef;
objdef.. obj =e= sum(i, p(i)) + x;

Model m /all/;
solve m using nlp minimizing obj;
