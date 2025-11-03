* Engineering Design with Fixed Variables Example
* Demonstrates: Fixed variables (x.fx) and design constraints
* Sprint 4 Feature: x.fx support creates equality constraints

Sets
    i Components /comp1*comp4/
;

Parameters
    minStrength Minimum strength requirement /100/
    maxWeight Maximum weight limit /50/
    unitCost(i) Cost per unit /comp1 5, comp2 8, comp3 12, comp4 15/
    strength(i) Strength contribution /comp1 20, comp2 35, comp3 50, comp4 60/
    weight(i) Weight per unit /comp1 8, comp2 12, comp3 15, comp4 18/
;

Variables
    x(i) Component quantities
    obj Total cost
    totalStrength Total strength
    totalWeight Total weight
;

Positive Variables x;

* Fix some components to specific values (design constraints)
* These become equality constraints in the MCP formulation
x.fx('comp1') = 2.0;    * Component 1 fixed at 2 units
x.fx('comp3') = 1.5;    * Component 3 fixed at 1.5 units

Equations
    objective Minimize total cost
    strengthReq Minimum strength requirement
    weightLimit Maximum weight constraint
    strengthCalc Calculate total strength
    weightCalc Calculate total weight
;

* Objective: minimize total cost
objective..
    obj =E= sum(i, unitCost(i) * x(i));

* Strength requirement
strengthReq..
    totalStrength =G= minStrength;

* Weight limit
weightLimit..
    totalWeight =L= maxWeight;

* Calculate total strength
strengthCalc..
    totalStrength =E= sum(i, strength(i) * x(i));

* Calculate total weight
weightCalc..
    totalWeight =E= sum(i, weight(i) * x(i));

* Initial guess for free variables
x.l('comp2') = 1.0;
x.l('comp4') = 0.5;

* Bounds for non-fixed variables
x.lo('comp2') = 0;
x.up('comp2') = 5;
x.lo('comp4') = 0;
x.up('comp4') = 3;

Model design /all/;
Solve design using NLP minimizing obj;

Display x.l, obj.l, totalStrength.l, totalWeight.l;

* Expected behavior:
* - x('comp1') remains at 2.0 (fixed)
* - x('comp3') remains at 1.5 (fixed)
* - x('comp2') and x('comp4') optimized
* - Constraints satisfied
* Note: Fixed variables create equality constraints paired with free multipliers
