# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-18 00:21:12
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
| circle | ❌ | - | - | ❌ | Parse error: ParserSemanticError |
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
| `UnexpectedCharacters` | 5 | himmel16, hs62, maxmin, mhw4dx, mingamma |
| `ParserSemanticError` | 3 | circle, mathopt1, trig |

**Note:** Convert and solve errors will appear here once those stages are implemented.

---

## Failure Details

### circle.gms
**Model:** circle
**Status:** Parse Failed
**Error Type:** `ParserSemanticError`
**Error Message:**
```
Assignments must use numeric constants; got Call(uniform, (Const(1.0), Const(10.0))) in assignment [context: expression]
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
No terminal matches 'a' in the current parser context, at line 63 col 11

elseif    abs(m.l-44.02207169) < tol, // local sol
          ^
Expected one of: 
	* DOT
	* __ANON_0
	* ASSIGN
	* LPAR
	* DOLLAR

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
