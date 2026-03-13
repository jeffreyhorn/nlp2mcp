# prolog: MCP Locally Infeasible — CES Demand Singular Jacobian

**GitHub Issue:** [#1070](https://github.com/jeffreyhorn/nlp2mcp/issues/1070)
**Model:** prolog (SEQ=124) — GAMS/MPSGE Prototype: Shoven-Whalley
**Type:** NLP
**Category:** KKT numerical conditioning (singular Jacobian from CES exponents)

---

## Summary

The prolog model is locally infeasible (model_status=5, 8060 iterations) because the CES (Constant Elasticity of Substitution) demand functions produce fractional exponents in the KKT stationarity equations that create singular Jacobian entries when variables approach zero or their lower bounds.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/prolog.gms -o data/gamslib/mcp/prolog_mcp.gms
cd /tmp && gams /path/to/data/gamslib/mcp/prolog_mcp.gms lo=2 o=prolog.lst
# Expected: MODEL STATUS 5 (Locally Infeasible), 8060 iterations
```

## Model Structure

- **Sets**: `i` (commodities: food, non-food), `h` (households: workers, capitalists), `k` (factors: labor, capital), `t` (technologies)
- **Objective**: Maximize consumer welfare (general equilibrium model)
- **Key primal variables**: `p(i)` (prices), `x(i,h)` (consumption), `y(h)` (income), `q(i,t)` (production), `r(k)` (factor returns)
- **CES demand constraint**: `dn(g,h).. x(g,h) =L= an(g,h) * prod(gp, p(gp)**eta(g,gp,h)) * y(h)**epsi(g,h)`
  - `eta(g,gp,h)` = price elasticities (can be negative)
  - `epsi(g,h)` = income elasticities (fractional, < 1 for some goods)

## Root Cause

### Singularity 1: `stat_y(h)` — Income variable

The derivative of the CES demand function w.r.t. `y(h)` produces:
```gams
y(h) ** epsi(g,h) * epsi(g,h) / y(h)
```
which equals `epsi(g,h) * y(h) ** (epsi(g,h) - 1)`.

When `epsi(g,h) < 1` (e.g., `epsi('food','workers') = 0.8`), the exponent `epsi - 1 = -0.2` creates a singularity at `y(h) = 0`: the gradient goes to infinity.

### Singularity 2: `stat_p(i)` — Price variable

The derivative of the CES demand function w.r.t. `p(gp)` produces terms like:
```gams
eta(g,gp,h) / p(gp) / p(gp) ** eta(g,gp,h)
```
which simplifies to `eta(g,gp,h) * p(gp) ** -(1 + eta(g,gp,h))`.

When `eta(g,gp,h) < -1`, the exponent becomes negative, creating a singularity at `p(gp) = 0` (or near the lower bound of 0.2).

### Effect on PATH solver

During MCP solution iterations, when variables approach zero or their lower bounds:
1. The Jacobian matrix entries become extremely large or undefined
2. Newton steps become unreliable
3. PATH cannot find a descent direction
4. After 8060 iterations, PATH reports locally infeasible with maximum residual of 1889 at `stat_p(food)`

## PATH Solver Output

```
MODEL STATUS      5 Locally Infeasible
SOLVER STATUS     1 Normal Completion
8060 iterations
Maximum residual: 1889 at stat_p(food)
```

## Fix Approach

1. **Variable substitution**: For CES power functions `y**epsi`, use a change of variables `log_y = log(y)` to eliminate the fractional exponent singularity. The derivative becomes `epsi * exp(epsi * log_y)` which is well-defined everywhere.
2. **Warm-start from NLP solution**: Initialize MCP variables from NLP solution to start PATH in a well-conditioned region away from singularities.
3. **Accept as known limitation**: CES models with fractional elasticities are inherently challenging for MCP/PATH due to non-smooth KKT systems. The original model is designed for MPSGE solver which handles these internally.

## Files

- `data/gamslib/raw/prolog.gms` — original NLP model
- `data/gamslib/mcp/prolog_mcp.gms` — generated MCP
- Key equations: `stat_y(h)`, `stat_p(i)` (singular Jacobian terms)
