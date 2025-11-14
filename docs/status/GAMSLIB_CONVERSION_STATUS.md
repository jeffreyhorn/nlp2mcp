# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-13 18:25:41
**Sprint:** Sprint 6
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint6.json`](../../reports/gamslib_ingestion_sprint6.json)

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 10.0% (1/10) | ≥10% | ✅ |
| **Convert Rate** | 0.0% (0/1) | ≥50% | ⚠️ Sprint 6: Not implemented |
| **Solve Rate** | 0.0% (0/0) | TBD | ⚠️ Sprint 6: Not implemented |
| **End-to-End** | 0.0% (0/10) | TBD | ⚠️ Sprint 6: Not implemented |

**Sprint 6 Target:** ✅ Parse ≥1 model (≥10% rate) - ✅ MET

---

## Model Status

| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| circle | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| himmel16 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| hs62 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| mathopt1 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| maxmin | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| mhw4d | ✅ | - | - | ❌ | Parsed successfully |
| mhw4dx | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| mingamma | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| rbrock | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| trig | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |

**Legend:**
- ✅ Success
- ❌ Failed
- `-` Not attempted (stage not implemented yet)

---

## Error Breakdown

### Parse Errors
| Error Type | Count | Models |
|------------|-------|--------|
| `UnexpectedCharacters` | 9 | circle, himmel16, hs62, mathopt1, maxmin, mhw4dx, mingamma, rbrock, trig |

**Note:** Convert and solve errors will appear here once those stages are implemented.

---

## Failure Details

### circle.gms
**Model:** circle
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches '$' in the current parser context, at line 16 col 1

$if not set size $set size 10
^
Expected one of: 
	* MODEL
	* SETS
	* EQUATIONS
	* SOLVE
	* SCALAR
	* POSITIVE_K
	* INTEGER_K
	* PARAMETER
	* EQUATION
	* PARAMETERS
	* BINARY_K
	* TABLE
	* VARIABLES
	* ID
	* VARIABLE
	* NEGATIVE_K
	* ALIASES
	* SCALARS
	* SEMI

```

### himmel16.gms
**Model:** himmel16
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'i' in the current parser context, at line 28 col 5

Set i 'indices for the 6 points' / 1*6 /;
    ^
Expected one of: 
	* ASSIGN
	* LPAR
	* DOT
	* __ANON_0

```

### hs62.gms
**Model:** hs62
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'm' in the current parser context, at line 35 col 4

   mx / objdef, eq1x /;
   ^
Expected one of: 
	* SEMI

```

### mathopt1.gms
**Model:** mathopt1
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'm' in the current parser context, at line 38 col 8

Models m / all /;
       ^
Expected one of: 
	* ASSIGN
	* SLASH
	* LPAR
	* DOT
	* SEMI
	* __ANON_0

```

### maxmin.gms
**Model:** maxmin
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches '$' in the current parser context, at line 28 col 1

$if not set points $set points 13
^
Expected one of: 
	* MODEL
	* SETS
	* EQUATIONS
	* SOLVE
	* SCALAR
	* POSITIVE_K
	* INTEGER_K
	* PARAMETER
	* EQUATION
	* PARAMETERS
	* BINARY_K
	* TABLE
	* VARIABLES
	* ID
	* VARIABLE
	* NEGATIVE_K
	* ALIASES
	* SCALARS
	* SEMI

```

### mhw4dx.gms
**Model:** mhw4dx
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'l' in the current parser context, at line 37 col 8

option limCol = 0, limRow = 0;
       ^
Expected one of: 
	* ASSIGN
	* LPAR
	* DOT
	* __ANON_0

```

### mingamma.gms
**Model:** mingamma
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'm' in the current parser context, at line 26 col 4

   m2 / y2def /;
   ^
Expected one of: 
	* SEMI

```

### rbrock.gms
**Model:** rbrock
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'm' in the current parser context, at line 24 col 15

solve rosenbr minimizing f using nlp;
              ^
Expected one of: 
	* USING

```

### trig.gms
**Model:** trig
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches ',' in the current parser context, at line 31 col 13

Scalar xdiff, fdiff;
            ^
Expected one of: 
	* ASSIGN
	* ID
	* SEMI
	* SLASH

```
