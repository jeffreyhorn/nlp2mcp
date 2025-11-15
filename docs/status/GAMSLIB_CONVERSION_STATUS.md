# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-15 16:35:46
**Sprint:** Sprint 6
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint6.json`](../../reports/gamslib_ingestion_sprint6.json)

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 10.0% (1/10) | ≥10% | ✅ |
| **Convert Rate** | 0.0% (0/1) | ≥50% | ⚠️ Sprint 6: Not implemented |
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
No terminal matches '1' in the current parser context, at line 25 col 16

x(i) = uniform(1,10);
               ^
Expected one of: 
	* ID

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
**Error Type:** `UnexpectedCharacters`
**Error Message:**
```
No terminal matches 'm' in the current parser context, at line 38 col 8

Models m / all /;
       ^
Expected one of: 
	* DOT
	* SLASH
	* SEMI
	* __ANON_0
	* ASSIGN
	* LPAR
	* DOLLAR

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
No terminal matches 'l' in the current parser context, at line 37 col 8

option limCol = 0, limRow = 0;
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
	* SEMI
	* ASSIGN
	* SLASH
	* ID

```
