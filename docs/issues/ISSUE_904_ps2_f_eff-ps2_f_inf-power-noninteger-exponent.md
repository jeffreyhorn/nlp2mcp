# ps2_f_eff / ps2_f_inf: `power()` Emitted with Non-Integer Exponent Causes Runtime Error

**GitHub Issue:** [#904](https://github.com/jeffreyhorn/nlp2mcp/issues/904)
**Model:** ps2_f_eff, ps2_f_inf (GAMSlib)
**Error category:** `path_solve_terminated`
**Runtime error:** `power: FUNC DOMAIN: pow(x,i), i not integer`
**Subcategory:** D (secondary — primary $445 already fixed)

## Description

Both models compile successfully after the Subcategory D ($445 negative exponent) fix, but fail at runtime. The AD engine's `_diff_power()` generates `Call("power", (base, Const(-0.5)))` when differentiating `x^0.5`. The emitter outputs this as `power(x(i), -0.5)`, but GAMS's `power()` function requires integer exponents. Non-integer exponents must use the `**` operator or `rpower()`.

Both models are structurally identical (same equations, same power expressions) and share the same root cause. They differ only in parameter values (`theta = 0.2` vs `0.3`).

## Reproduction

```bash
# Models compile but fail at runtime:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
    data/gamslib/mcp/ps2_f_eff_mcp.gms lo=3 o=/tmp/ps2_f_eff_test.lst

grep 'FUNC DOMAIN' /tmp/ps2_f_eff_test.lst
```

Output:
```
*** Exec Error at line 103: power: FUNC DOMAIN: pow(x,i), i not integer
*** Evaluation error(s) in equation "stat_x(eff)"
        Problem in Jacobian evaluation of "nu_rev(eff)"
```

## GAMS Source Context — Original Equation

```gams
* Original NLP equation (ps2_f_eff.gms, line ~26):
rev(i).. b(i) =e= x(i)**(0.5);
```

## Emitted MCP — Offending Stationarity Equation

```gams
* AD-generated stationarity (ps2_f_eff_mcp.gms, line 103):
stat_x(i).. ((-1) * (0.5 * power(x(i), -0.5))) * nu_rev(i)
          + ((-1) * theta(i)) * nu_pc(i) - piL_x(i) =E= 0;
```

The `power(x(i), -0.5)` call is invalid because `-0.5` is not an integer.

## Root Cause

**Chain of events:**
1. Parser stores `x(i)**(0.5)` as `Binary("**", VarRef("x"), Const(0.5))`
2. AD engine in `_diff_power()` (`src/ad/derivative_rules.py`, line 678) applies constant-exponent rule: `d/dx[x^0.5] = 0.5 * power(x, -0.5)`
3. Result AST: `Call("power", (VarRef("x"), Const(-0.5)))`
4. Emitter guard (`src/emit/expr_to_gams.py`, lines 545–557) only converts `power()` to `**` when the exponent is NOT a `Const` or `ParamRef` — but here the exponent IS a `Const(-0.5)`, so it passes through
5. Emitter outputs `power(x(i), -0.5)` — invalid at runtime

**The bug is in the emitter guard logic:** it assumes `Const` exponents in `power()` are always integers, but the AD engine can produce non-integer `Const` exponents from differentiation.

## Scope

This same `power(base, non-integer-const)` pattern affects at least 13 models in the MCP cache:
- ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s
- ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp
- ps5_s_mn, ps10_s, ps10_s_mn
- launch (has non-integer exponents like `-0.214`, `-0.668`, `-0.892`)

## Fix Approach

Enhance the emitter guard in `src/emit/expr_to_gams.py` (~line 545) to check if a `Const` exponent is non-integer:

```python
if func == "power" and len(args) == 2:
    exponent = args[1]
    use_infix = not isinstance(exponent, (Const, ParamRef))
    # Also use ** for non-integer constant exponents
    if isinstance(exponent, Const) and float(exponent.value) != int(exponent.value):
        use_infix = True
    if use_infix:
        # emit as base ** exponent
```

This converts `power(x(i), -0.5)` → `x(i) ** (-0.5)`, which GAMS handles correctly. The existing negative-exponent parenthesization fix (from PR #900) ensures the negative sign is wrapped in parentheses.

**Estimated effort:** 30min (emitter guard fix + tests)

## Related Issues

- Primary Subcategory D ($445 negative exponent) already fixed in PR #900
- The `**` operator with negative exponents already works correctly (tested in PR #900)
- `ParamRef` exponents should also use `**` (they might be non-integer at runtime)
