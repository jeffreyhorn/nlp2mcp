# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-18 00:48:05
**Sprint:** Sprint 6
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint6.json`](../../reports/gamslib_ingestion_sprint6.json)

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 20.0% (2/10) | ≥10% | ✅ |
| **Convert Rate** | 0.0% (0/2) | ≥50% | ⚠️ Sprint 6: Not implemented |
| **Solve Rate** | 0.0% (N/A) | TBD | ⚠️ Sprint 6: Not implemented |
| **End-to-End** | 0.0% (0/10) | TBD | ⚠️ Sprint 6: Not implemented |

**Sprint 6 Target:** ✅ Parse ≥1 model (≥10% rate) - ✅ MET

---

## Model Status

| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| circle | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| himmel16 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| hs62 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| mathopt1 | ❌ | - | - | ❌ | Parse error: ParserSemanticError |
| maxmin | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| mhw4d | ✅ | - | - | ❌ | Parsed successfully |
| mhw4dx | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| mingamma | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
| rbrock | ✅ | - | - | ❌ | Parsed successfully |
| trig | ❌ | - | - | ❌ | Parse error: ParserSemanticError |

**Legend:**
- ✅ Success
- ❌ Failed
- `-` Not attempted (stage not implemented yet)

---

## Error Breakdown

### Parse Errors
| Error Type | Count | Models |
|------------|-------|--------|
| `UnexpectedCharacters` | 6 | circle, himmel16, hs62, maxmin, mhw4dx, mingamma |
| `ParserSemanticError` | 2 | mathopt1, trig |

**Note:** Convert and solve errors will appear here once those stages are implemented.

---

## Failure Details

### circle.gms
**Model:** circle
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'm' in the current parser context, at line 54 col 6

if(m.modelStat <> %modelStat.optimal%        
     ^
Expected one of: 
	* BOUND_K

```

### himmel16.gms
**Model:** himmel16
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches '+' in the current parser context, at line 46 col 39

areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));
                                      ^
Expected one of: 
	* RPAR
	* COMMA

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
**Error Type:** `ParserSemanticError`
**Error Message:**
```
Indexed assignments are not supported yet [context: expression] (line 45, column 1)
```

### maxmin.gms
**Model:** maxmin
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches '(' in the current parser context, at line 51 col 12

defdist(low(n,nn))..   dist(low) =e= sqrt(sum(d, sq
           ^
Expected one of: 
	* RPAR
	* COMMA

```

### mhw4dx.gms
**Model:** mhw4dx
**Status:** Parse Failed
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'm' in the current parser context, at line 62 col 18

   abort$(wright.modelStat = %modelStat.optimal%) 'solver
                 ^
Expected one of: 
	* BOUND_K

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

### trig.gms
**Model:** trig
**Status:** Parse Failed
**Error Type:** `ParserSemanticError`
**Error Message:**
```
Unsupported expression type: bound_scalar. This may be a parser bug or unsupported GAMS syntax. Supported: variables, parameters, numbers, operators (+, -, *, /, ^), functions (sqrt, exp, log, etc.), sum(). [context: assignment] (line 32, column 23)
```
