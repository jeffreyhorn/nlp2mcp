* Test Case 3 Manual MCP: minimize z where z = max(x, y) (opposite sense)
* Strategy 2 reformulation: z >= x, z >= y
* Question: Will minimization push z down to max(x,y)?

Variables
    x         primal variable
    y         primal variable
    z         objective variable
    obj       objective value
    lam_x     multiplier for z >= x (x - z <= 0)
    lam_y     multiplier for z >= y (y - z <= 0)
    piL_x     multiplier for x >= 1
    piU_x     multiplier for x <= 10
    piL_y     multiplier for y >= 2
    piU_y     multiplier for y <= 10
    nu_obj    multiplier for obj = z
;

Positive Variables lam_x, lam_y, piL_x, piU_x, piL_y, piU_y;

Equations
    stat_x       stationarity for x
    stat_y       stationarity for y
    stat_z       stationarity for z
    stat_obj     stationarity for obj
    ineq_x_le_z  inequality x <= z
    ineq_y_le_z  inequality y <= z
    eq_obj       equality obj = z
;

* Stationarity equations
* dL/dx = lam_x + piL_x - piU_x = 0
stat_x.. lam_x + piL_x - piU_x =E= 0;

* dL/dy = lam_y + piL_y - piU_y = 0
stat_y.. lam_y + piL_y - piU_y =E= 0;

* dL/dz = 1 - nu_obj - lam_x - lam_y = 0
stat_z.. 1 - nu_obj - lam_x - lam_y =E= 0;

* dL/dobj = nu_obj = 0
stat_obj.. nu_obj =E= 0;

* Inequality constraints (z >= x and z >= y)
ineq_x_le_z.. x - z =L= 0;
ineq_y_le_z.. y - z =L= 0;

* Equality constraint
eq_obj.. obj - z =E= 0;

* Bounds
x.lo = 1;  x.up = 10;
y.lo = 2;  y.up = 10;

* Initial values
x.l = 5;
y.l = 5;
z.l = 5;
obj.l = 5;

Model test_mcp /
    stat_x.x
    stat_y.y
    stat_z.z
    stat_obj.obj
    ineq_x_le_z.lam_x
    ineq_y_le_z.lam_y
    eq_obj.nu_obj
/;

Solve test_mcp using MCP;

Display x.l, y.l, z.l, obj.l, lam_x.l, lam_y.l;
Display "Expected: z = 2 (max of lower bounds), both lam > 0";
