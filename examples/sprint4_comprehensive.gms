* Comprehensive Sprint 4 Features Example
* Demonstrates: All Sprint 4 features in one model
* Features: $include, Table, min/max, abs(), x.fx, scaling

* Use $include for modular model structure
$include sprint4_comprehensive_data.gms

Sets
    t Time periods /t1*t4/
;

Variables
    production(t) Production in each period
    inventory(t) Inventory at end of period
    shortage(t) Shortage in each period
    obj Total cost
    maxShortage Maximum shortage across all periods
;

Positive Variables production, inventory, shortage;

* Fix initial inventory
inventory.fx('t1') = initialInventory;

Equations
    objective Total cost minimization
    balance(t) Inventory balance
    minProduction(t) Minimum production using min()
    maxShortageCalc Calculate maximum shortage
    capacityLimit(t) Production capacity
;

* Objective: production cost + inventory cost + shortage penalty
* Uses max() to penalize worst shortage period
objective..
    obj =E= sum(t, productionCost(t) * production(t)
                 + inventoryCost * inventory(t))
          + shortagepenalty * maxShortage;

* Inventory balance equation
balance(t)..
    inventory(t) =E= inventory(t-1) + production(t) - demand(t);

* Minimum production constraint: use min(demand, capacity)
* Demonstrates min() in constraint
minProduction(t)..
    production(t) =G= min(demand(t), capacity(t)) * 0.5;

* Calculate maximum shortage across all time periods
* Multi-argument max() demonstration
maxShortageCalc..
    maxShortage =E= max(shortage('t1'), shortage('t2'),
                        shortage('t3'), shortage('t4'));

* Production capacity (varies by period)
capacityLimit(t)..
    production(t) =L= capacity(t);

* Initial values
production.l(t) = demand(t);
inventory.l(t) = 50;

Model comprehensive /all/;
Solve comprehensive using NLP minimizing obj;

Display production.l, inventory.l, shortage.l, obj.l, maxShortage.l;

* Run with Sprint 4 features:
* nlp2mcp sprint4_comprehensive.gms -o output.gms --scale auto --stats
*
* This model demonstrates:
* 1. $include directive (modular data)
* 2. Table data blocks (in included file)
* 3. min() function (minProduction constraint)
* 4. max() function (maxShortageCalc equation)
* 5. Fixed variables (inventory.fx)
* 6. Scaling recommendation (--scale auto for production/inventory magnitudes)
* 7. Diagnostics (--stats shows model size)
