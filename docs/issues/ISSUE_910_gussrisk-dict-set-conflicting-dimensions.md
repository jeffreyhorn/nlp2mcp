# gussrisk: GUSS Dict Set Conflicting Dimensions ($161)

**GitHub Issue:** [#910](https://github.com/jeffreyhorn/nlp2mcp/issues/910)
**Model:** gussrisk (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $161 Conflicting dimensions in element

## Problem

The generated MCP file declares a `dict` set with multi-dimensional dotted labels that GAMS interprets as tuple references rather than literal labels:

```gams
Sets
    dict /'rapscenarios.scenario.', rap.param.riskaver, invest.level.stockoutput,
           obj.level.objlevel, investav.marginal.investavshadow/
;
```

GAMS produces 4 `$161` errors because each dotted element (e.g., `rap.param.riskaver`) is interpreted as a 3-dimensional tuple, conflicting with the 1-dimensional `dict` set declaration. These are literal text labels used by the GUSS (Generalized Uncertain Scenario Solution) framework, not actual multi-dimensional references.

## Error Output

```
**** 161  Conflicting dimensions in element
```

4 compilation errors + 2 downstream errors ($257 solve not checked, $141 no values assigned).

## Root Cause

The original gussrisk.gms (lines 85-89) declares a `dict` set for the GUSS solver option. The GUSS dict set uses a special syntax where elements like `rapscenarios.scenario.` are literal labels encoding scenario-parameter-attribute triples. The parser/emitter does not recognize the GUSS `dict` pattern and treats these as regular set elements with dotted references.

## Original GAMS

```gams
Set dict / rapscenarios.scenario.'',
           rap      .param   .riskaver,
           invest   .level   .stockoutput,
           obj      .level   .objlevel,
           investav .marginal.investavshadow /;
```

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/gussrisk.gms -o /tmp/gussrisk_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/gussrisk_mcp.gms o=/tmp/gussrisk_mcp.lst
grep '^\*\*\*\*' /tmp/gussrisk_mcp.lst
```

## Suggested Fix

The GUSS `dict` set uses a 3-column table format with implicit `.`-separated structure. Options:
1. **Detect and skip GUSS dict sets** — if the model uses `solve ... scenario dict`, skip the dict set from MCP transformation
2. **Emit dict elements as quoted strings** — wrap each dotted label in single quotes
3. **Flag as unsupported** — GUSS models require special handling beyond static KKT transformation

## Impact

6 total errors (4 primary + 2 downstream). Model cannot compile.
