* Test Case 1 Manual MCP: minimize z where z = min(x, y)
* Strategy 2 reformulation: z <= x, z <= y
*
* CRITICAL FINDING: This formulation is INFEASIBLE!
* The stationarity equation for z requires: 1 + lam_x + lam_y = 0
* This means lam_x + lam_y = -1
* But lam_x, lam_y >= 0 (they're multipliers for inequalities)
* Therefore, this system has NO SOLUTION.
*
* This confirms the research doc's analysis that Strategy 2 FAILS
* when min appears in an objective-defining equation with minimization.

Variables
    x         primal variable
    y         primal variable
    z         objective variable (free)
    lam_x     multiplier for z - x <= 0
    lam_y     multiplier for z - y <= 0
;

* Set bounds on primal variables
x.lo = 1;  x.up = 10;
y.lo = 2;  y.up = 10;

Equations
    stat_x       stationarity for x
    stat_y       stationarity for y
    stat_z       stationarity for z
    feas_z_x     feasibility z - x <= 0
    feas_z_y     feasibility z - y <= 0
;

* Stationarity equations
* dL/dx = -lam_x = 0 (ignoring bound multipliers for simplicity)
stat_x.. -lam_x =E= 0;

* dL/dy = -lam_y = 0
stat_y.. -lam_y =E= 0;

* dL/dz = 1 + lam_x + lam_y = 0
* This is the INFEASIBLE equation: requires lam_x + lam_y = -1
stat_z.. 1 + lam_x + lam_y =E= 0;

* Feasibility constraints (matched with multipliers via .lam_x and .lam_y)
feas_z_x.. z - x =L= 0;
feas_z_y.. z - y =L= 0;

* Initial values (will fail to solve)
x.l = 5;
y.l = 5;
z.l = 2;

Model test_mcp /
    stat_x.x
    stat_y.y
    stat_z.z
    feas_z_x.lam_x
    feas_z_y.lam_y
/;

* Note: This will fail to solve or give infeasible status
Solve test_mcp using MCP;

Display x.l, y.l, z.l, lam_x.l, lam_y.l;
Display "EXPECTED RESULT: Infeasible or no solution found";
Display "REASON: stat_z requires lam_x + lam_y = -1, but both must be >= 0";
Display "CONCLUSION: Strategy 2 (direct constraints) DOES NOT WORK for minimize z where z = min(x,y)";
