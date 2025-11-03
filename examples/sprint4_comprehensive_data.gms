* Data file for comprehensive Sprint 4 example
* Demonstrates: Table data blocks and parameter declarations

Parameters
    initialInventory Initial inventory level /100/
    inventoryCost Cost per unit of inventory /2/
    shortagePenalty Penalty for shortage /50/
;

* Demand data using Table (Sprint 4 feature)
Table demand(t) Demand by time period
         t1   t2   t3   t4
    demand 120  150  180  140
;

* Production costs by period using Table
Table productionCost(t) Production cost by period
              t1   t2   t3   t4
    prodCost  10   12   11   13
;

* Production capacity by period using Table
Table capacity(t) Production capacity by period
           t1   t2   t3   t4
    cap   200  180  220  190
;
