# Parser: Set Member Validation Too Strict (Case Sensitivity)

## GitHub Issue
- **Issue #:** 435
- **URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/435

## Summary
The semantic validation for parameter data is too strict when checking set member references, failing on case mismatches that GAMS accepts.

## Affected Model
- **chem.gms** (Tier 2) - Chemical Equilibrium Problem

## Error
```
Parameter 'mix' references member 'h' not present in set 'i' [context: expression] (line 25, column 47)
```

## Root Cause
The validation checks if parameter data keys reference valid set members, but the comparison is case-sensitive. GAMS identifiers are case-insensitive.

## GAMS Code Pattern
```gams
Set c  'species' / H, H2, H2O, N, N2, NH, NO, O, O2, OH /;

Parameter
   mix(i)   'number of elements in mixture' / h 2, n 1, o 1 /
   gibbs(c) 'gibbs free energy at 3500 k and 750 psi'
            / H  -10.021, H2  -21.096, H2O -37.986, N   -9.846, N2 -28.653
              NH -18.918, NO -28.032 , O   -14.640, o2 -30.594, OH -26.11  /;
```

Note that:
- Set `c` defines `H` (uppercase)
- Parameter `mix` references `h` (lowercase)
- Parameter `gibbs` uses `o2` (lowercase) while set has `O2` (uppercase)

GAMS treats these as equivalent due to case-insensitivity.

## Current Behavior
The parser/validator compares set members with exact case matching, causing `'h'` to not match `'H'`.

## Suggested Fix
Make set member validation case-insensitive:
1. Normalize both set member names and parameter data keys to lowercase during comparison
2. Or use a case-insensitive comparison function

## Complexity
Low - simple string comparison change in validation logic.

## Test Case
```gams
Set i / A, B, C /;
Parameter p(i) / a 1, b 2, c 3 /;
```

Expected: Parse succeeds with case-insensitive matching of `a`→`A`, `b`→`B`, `c`→`C`.
