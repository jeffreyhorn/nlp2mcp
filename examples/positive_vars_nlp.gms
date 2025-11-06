* Example NLP with Positive Variables keyword (Issue #140)
* Demonstrates block-level variable kind declaration
*
* This is a simple quadratic optimization problem where we minimize
* the sum of weighted squared variables subject to meeting a total demand.
* The Positive Variables keyword ensures all variables are non-negative.

Sets
    i /i1*i3/ ;

Parameters
    c(i) /i1 1.0, i2 2.0, i3 3.0/ ;

Scalars
    demand /3.0/ ;

Positive Variables
    x(i)
    obj ;

Equations
    objective
    total_demand ;

objective.. obj =e= sum(i, c(i) * x(i) * x(i));

total_demand.. sum(i, x(i)) =e= demand;

Model positive_vars_example / all / ;
Solve positive_vars_example using NLP minimizing obj;
