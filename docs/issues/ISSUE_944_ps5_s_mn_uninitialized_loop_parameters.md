# ps5_s_mn: Uninitialized Parameters from Multi-Solve Loop Pattern

**GitHub Issue:** [#944](https://github.com/jeffreyhorn/nlp2mcp/issues/944)
**Status:** OPEN
**Models:** ps5_s_mn (GAMSlib)
**Error category:** `gams_compilation_error` (Error 141, then Error 257)
**Compilation error:** `Symbol declared but no values have been assigned`

## Description

The ps5_s_mn model uses a `loop(t, ...)` with embedded `solve` statements that populate parameters (`Util_lic`, `Util_lic2`, `MN_lic`, `pt`) used later in display/comparison logic. The NLP-to-MCP transformation cannot handle this multi-solve pattern because:

1. The parameters `pt(i,t)` are initialized via `uniform()` inside a loop — the transformer doesn't execute procedural GAMS code
2. `Util_lic(t)`, `Util_lic2(t)`, `MN_lic(t)`, `MN_lic2(t)` are populated by `.l` values from solve statements inside the loop — these values don't exist in the MCP
3. The generated MCP declares these parameters but never assigns them, causing GAMS Error 141

## Reproduction

```bash
# Translate and solve:
python -m src.cli data/gamslib/raw/ps5_s_mn.gms -o /tmp/ps5_s_mn_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/ps5_s_mn_mcp.gms lo=2

# Expected errors:
# **** 141  Symbol declared but no values have been assigned.
#   Util_lic2, MN_lic, pt
# **** 257  Solve statement not checked because of previous errors
```

## Root Cause

The original model has this structure:

```gams
* 1. Random initialization:
loop(t, pt(i,t) = uniform(0,1););
pt(i,t) = pt(i,t) / sum(j, pt(j,t));

* 2. Multi-solve loop:
loop(t,
   p(i) = pt(i,t);          ← assigns from pt
   solve ps5_s ... min util; ← first solve
   Util_lic(t) = util.l;    ← captures optimal value
   MN_lic(t) = sum(i, 1$(round(x.l(i),10) < round(x.l(i+1),10)));
   solve ps5_mn ... min util; ← second solve (with monotonicity constraint)
   Util_lic2(t) = util.l;
   MN_lic2(t) = ...;
);

* 3. Post-loop comparison:
Util_gap(t) = 1$(round(Util_lic(t),10) <> round(Util_Lic2(t),10));
p_noMN_lic = sum(t$(MN_lic(t) > 0), 1) / card(t) * 100;
```

The NLP-to-MCP transformer:
- Declares all parameters (pt, Util_lic, etc.) because they appear in the model
- Cannot execute `uniform()` or solve loops
- Cannot populate solve-dependent parameters
- Emits the post-loop comparison code that references uninitialized parameters

## Emitted MCP — Offending Lines

```gams
Parameters
    pt(i,t)           * declared but never assigned (populated by uniform() in original)
    Util_lic(t)       * declared but never assigned (populated by solve loop)
    Util_lic2(t)      * declared but never assigned (populated by solve loop)
    MN_lic(t)         * declared but never assigned (populated by solve loop)
;

* These lines reference uninitialized parameters:
Util_gap(t) = 1$(round(Util_lic(t), 10) <> round(Util_Lic2(t), 10));  ← Error 141
p_noMN_lic = sum(t$(MN_lic(t) > 0), 1) / card(t) * 100;              ← Error 141
F(i,t) = sum(j$(ord(j) <= ord(i)), pt(j,t));                          ← Error 141
```

## Fix Approach

This model is **fundamentally incompatible** with the single-model MCP transformation approach. The original model's purpose is to compare solutions with and without monotonicity constraints across random scenarios — it solves the NLP multiple times with different data.

**Option A (Partial): Strip post-solve comparison code.** The post-loop comparison code (`Util_gap`, `p_noMN_lic`, `F`, `noMHRC0`) is not part of the optimization model itself. The emitter could:
1. Identify parameters only assigned inside solve loops or via `uniform()`
2. Skip post-solve display/comparison code that depends on these parameters
3. Focus on translating just the core NLP optimization problem

**Option B: Document as unsupported pattern.** Multi-solve models with loop-embedded solves are a fundamentally different use case (Monte Carlo simulation, scenario comparison). These cannot be meaningfully converted to a single MCP. Document this as a known limitation.

**Estimated effort:** Option A: 2-3h; Option B: 15min

## Related Issues

- #904: power() non-integer exponent (primary blocker now fixed; this is the secondary blocker)
- Multi-solve loop pattern may affect other GAMSlib models (not yet surveyed)
