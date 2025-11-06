* Test Case 4 Manual MCP: maximize z where z = min(x, y) (opposite sense)
* Strategy 2 reformulation: z <= x, z <= y
* Question: Will maximization push z up to min(x,y)?

Variables
    x         primal variable
    y         primal variable
    z         objective variable
    obj       objective value
    lam_x     multiplier for z <= x
    lam_y     multiplier for z <= y
    piL_x     multiplier for x >= 0
    piU_x     multiplier for x <= 10
    piL_y     multiplier for y >= 0
    piU_y     multiplier for y <= 15
    nu_obj    multiplier for obj = z
;

Positive Variables lam_x, lam_y, piL_x, piU_x, piL_y, piU_y;

Equations
    stat_x       stationarity for x
    stat_y       stationarity for y
    stat_z       stationarity for z
    stat_obj     stationarity for obj
    ineq_z_le_x  inequality z <= x
    ineq_z_le_y  inequality z <= y
    eq_obj       equality obj = z
;

* Stationarity equations
* For maximization, objective gradient is -1
* dL/dx = -lam_x + piL_x - piU_x = 0
stat_x.. -lam_x + piL_x - piU_x =E= 0;

* dL/dy = -lam_y + piL_y - piU_y = 0
stat_y.. -lam_y + piL_y - piU_y =E= 0;

* dL/dz = -1 - nu_obj + lam_x + lam_y = 0 (negative obj gradient for max)
stat_z.. -1 - nu_obj + lam_x + lam_y =E= 0;

* dL/dobj = nu_obj = 0
stat_obj.. nu_obj =E= 0;

* Inequality constraints (z <= x and z <= y)
ineq_z_le_x.. z - x =L= 0;
ineq_z_le_y.. z - y =L= 0;

* Equality constraint
eq_obj.. obj - z =E= 0;

* Bounds
x.lo = 0;  x.up = 10;
y.lo = 0;  y.up = 15;

* Initial values
x.l = 5;
y.l = 7;
z.l = 5;
obj.l = 5;

Model test_mcp /
    stat_x.x
    stat_y.y
    stat_z.z
    stat_obj.obj
    ineq_z_le_x.lam_x
    ineq_z_le_y.lam_y
    eq_obj.nu_obj
/;

Solve test_mcp using MCP;

Display x.l, y.l, z.l, obj.l, lam_x.l, lam_y.l;
Display "Expected: z = 10 (min of upper bounds), both lam > 0";
