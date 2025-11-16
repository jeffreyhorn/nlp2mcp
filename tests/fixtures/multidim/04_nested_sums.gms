$onText
Fixture 04: Nested Sum Patterns
Tests: Nested summations over multi-dimensional variables
$offText

Sets
    i "set 1" /i1*i3/
    j "set 2" /j1*j2/;

Parameters
    demand(i) "demand at each i";

Variables
    flow(i,j) "flow from i to j"
    total "total flow";

Equations
    obj_def "Objective"
    demand_constraint(i) "Demand must be met";

* Objective: minimize total flow
obj_def.. total =e= sum(i, sum(j, flow(i,j)));

* Demand constraint: sum over j for each i
demand_constraint(i).. sum(j, flow(i,j)) =e= demand(i);

Model nested_sums /all/;
Solve nested_sums using nlp minimizing total;
