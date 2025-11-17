$onText
Fixture 05: Transportation Problem (Classic 2D)
Tests: Real-world 2D pattern - supply, demand, and flow
$offText

Sets
    plants "supply points" /seattle, sandiego/
    markets "demand points" /newyork, chicago, topeka/;

Parameters
    capacity(plants) "plant capacity"
    demand(markets) "market demand";

Variables
    x(plants, markets) "shipment quantities"
    z "total transportation cost";

Equations
    obj "objective function"
    supply(plants) "supply limit"
    satisfy(markets) "demand requirement";

* Objective: minimize total (using placeholder cost of 1)
obj.. z =e= sum(plants, sum(markets, x(plants, markets)));

* Supply constraints
supply(plants).. sum(markets, x(plants, markets)) =l= capacity(plants);

* Demand constraints
satisfy(markets).. sum(plants, x(plants, markets)) =g= demand(markets);

Model transport /all/;
Solve transport using nlp minimizing z;
