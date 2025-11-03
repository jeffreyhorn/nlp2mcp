* Production Planning with min/max Reformulation Example
* Demonstrates: min() and max() functions in objective and constraints
* Sprint 4 Feature: Non-smooth function reformulation

Sets
    i Products /prod1*prod3/
    j Resources /labor, material, machine/
;

Parameters
    demand(i) Product demands /prod1 100, prod2 150, prod3 80/
    capacity(j) Resource capacities /labor 500, material 800, machine 400/
    unitCost(i) Unit production costs /prod1 10, prod2 12, prod3 15/
    resourceUse(i,j) Resource usage per unit
        /prod1.labor 2, prod1.material 3, prod1.machine 1
         prod2.labor 3, prod2.material 2, prod2.machine 2
         prod3.labor 1, prod3.material 4, prod3.machine 3/
;

Variables
    x(i) Production quantities
    obj Objective value
    shortage Total shortage cost
    maxShortage Maximum shortage across products
;

Positive Variables x, shortage, maxShortage;

Equations
    objective Define objective
    resourceLimit(j) Resource capacity constraints
    shortageCalc Total shortage calculation
    maxShortageCalc Maximum shortage calculation
;

* Objective: minimize production cost + penalty for maximum shortage
* Uses max() to penalize the worst shortage
objective..
    obj =E= sum(i, unitCost(i) * x(i)) + 100 * maxShortage;

* Resource constraints
resourceLimit(j)..
    sum(i, resourceUse(i,j) * x(i)) =L= capacity(j);

* Total shortage using max(0, demand - production)
* Demonstrates max() in equation
shortageCalc..
    shortage =E= sum(i, max(0, demand(i) - x(i)));

* Maximum shortage across all products
* Demonstrates multi-argument max()
maxShortageCalc..
    maxShortage =E= max(demand('prod1') - x('prod1'),
                        demand('prod2') - x('prod2'),
                        demand('prod3') - x('prod3'),
                        0);

* Initial values
x.l(i) = demand(i) * 0.8;

Model production /all/;
Solve production using NLP minimizing obj;

Display x.l, obj.l, shortage.l, maxShortage.l;
