# path_syntax_error Root Cause Catalog (45 Models)

**Created:** 2026-02-24
**Sprint:** 21 (Priority 3 workstream)
**Budget:** 8-12h
**Status:** Catalog complete, ready for Sprint 21 execution

---

## 1. Executive Summary

All 45 path_syntax_error models were compiled through GAMS v53, and the compilation errors were captured and classified. The errors fall into **9 distinct root cause subcategories**, with **missing parameter/Table data** being the dominant blocker (16/45 models). The top 3 subcategories account for 32/45 models (71%), confirming that a small number of fixes can address the majority of failures.

### Root Cause Distribution

| Subcategory | Root Cause | Models | Count | Stage | Est. Effort |
|-------------|-----------|--------|-------|-------|-------------|
| A | Missing parameter/Table data | 16 | 16 | Parser (IR builder) | 4-6h |
| B | Domain violation in emitted parameter data | 5 | 5 | Emitter (data formatting) | 2-3h |
| C | Uncontrolled set in stationarity equations | 9 | 9 | Translator (KKT generation) | 3-5h |
| D | Negative exponent needs parentheses (`** -N`) | 3 | 3 | Emitter (expression formatting) | 1h |
| E | Set index quoted as string literal | 7 | 7 | Emitter (identifier quoting) | 1-2h |
| F | GAMS built-in function name collision | 1 | 1 | Translator (identifier naming) | 1h |
| G | Set index reuse conflict in sum | 2 | 2 | Translator (sum domain handling) | 1-2h |
| I | MCP variable not referenced in equations | 1 | 1 | Translator (MCP model statement) | 1h |
| J | Equation-variable dimension mismatch | 1 | 1 | Translator (equation-variable pairing) | 1h |

**Total estimated effort: 15-22h** (above the 8-12h budget; triage recommended)

### Key Findings

1. **Missing parameter/Table data is the primary blocker** (16/45 models) — the IR builder does not capture Table data blocks into `ParameterDef.values`, so the emitter outputs declarations without data
2. **Top 3 subcategories (A + C + E) account for 32/45 models** (71%) — fixing these three issues would address the vast majority of failures
3. **Errors span all three pipeline stages**: parser (16 models), translator (14 models), emitter (15 models)
4. **Several subcategories have single-fix potential**: Subcategory D (parenthesizing negative exponents) and E (fixing set index quoting) are simple emitter fixes with high leverage

---

## 2. Subcategory Details

### 2.1 Subcategory A: Missing Parameter/Table Data (16 models)

**GAMS Error Codes:** $141 (symbol declared but no values assigned), $66 (symbol not defined — cascading)
**Pipeline Stage:** Parser (IR builder)
**Models:** gussrisk, hydro, iobalance, least, lmp2, marco, markov, mine, otpop, paperco, ps10_s_mn, ps5_s_mn, qdemo7, ship, sroute, tforss

**Root Cause:**
The IR builder (`src/ir/parser.py`) does not capture `Table` data blocks into `ParameterDef.values`. When the emitter outputs the MCP file, these parameters are declared but have no data assigned. GAMS then raises $141 when these empty parameters are referenced in assignments or equations.

**Example (iobalance):**
```gams
* Original NLP (has Table data):
Table z1(i,j) 'unknown industry flows'
       1   2   3
   1  98  72  75
   2  65   8  63
   3  88  27  44;

* Generated MCP (declaration only, no data):
Parameters
    z1(i,j)
;
u(i) = sum(j, z1(i,j));  ← $141: z1 has no values
```

**Verification:** Confirmed by checking `ParameterDef.values` for `z1` in iobalance's parsed IR — returns empty dict `{}` despite the Table having data in the original file.

**Sub-patterns within A:**
- **Table data not parsed** (majority): iobalance (`z1`), least (`dat`), qdemo7 (`alpha`), etc.
- **Ordering issue** (minority): marco (`phi.l` used before Solve), lmp2 (`n(nn)` subset used before assignment)
- **$66 at Solve statement** (5 models: least, markov, mine, paperco, tforss): The model compiles but GAMS can't resolve equation references because data parameters used in equations are empty

**Fix:** Enhance the IR builder to capture Table data into `ParameterDef.values`. This is a parser-stage fix that would unblock all 16 models (pending any secondary errors).

**Estimated Effort:** 4-6h (Table parsing is complex due to multi-line format, dotted indices, and column headers)

---

### 2.2 Subcategory B: Domain Violation in Emitted Parameter Data (5 models)

**GAMS Error Code:** $170 (domain violation for element)
**Pipeline Stage:** Emitter (data formatting)
**Models:** agreste, china, egypt, fawley, gtm

**Root Cause:**
The emitter outputs parameter data with set elements that do not belong to the parameter's declared domain. This happens when the IR builder stores data with incorrect domain mapping, or when the emitter fails to filter out-of-domain entries.

**Example (agreste):**
```gams
* labor(p,tm) declared with domain (p, tm)
* But emitted data includes: nov.jan 0, nov.feb 0, ...
* 'nov' is an element of 'tm', not 'p' → domain violation
labor(p,tm) /..., nov.jan 0, nov.feb 0, .../
                  ^^^               ← $170: 'nov' not in set p
```

**Example (egypt):**
```gams
* regwat(r,tm) declared with domain (r, tm)
* But emitted data includes: apr.nov 0, apr.dec 0, ...
* 'apr' is an element of 'tm', not 'r' → domain violation
regwat(r,tm) /..., apr.nov 0, apr.dec 0, .../
                   ^^^              ← $170: 'apr' not in set r
```

**Fix:** Fix the emitter's domain mapping for parameter data — ensure that data entries are emitted with the correct domain assignment, filtering or reordering entries that violate domain constraints.

**Estimated Effort:** 2-3h

---

### 2.3 Subcategory C: Uncontrolled Set in Stationarity Equations (9 models)

**GAMS Error Code:** $149 (uncontrolled set entered as constant)
**Pipeline Stage:** Translator (KKT generation)
**Models:** ampl, dyncge, glider, harker, korcge, paklive, robert, shale, tabora

**Root Cause:**
The translator generates stationarity equations (∂L/∂x = 0) that reference set indices outside their controlling domain. When a variable `x(i)` participates in an equation that sums over set `j`, the stationarity equation for `x(i)` should only reference `i` as a free index — but the translator emits references to `j` (or other sets) as uncontrolled constants.

**Example (dyncge):**
```gams
* stat_epsilon is a scalar equation (no domain)
* But references pf(h,j) where h is not in a sum — $149
stat_epsilon.. ... + sum(j, ((-1) * (pf(h,j) ** zeta * f(h,j) /
                                     sum(i, pf(h,i) ** zeta * f(h,i)) * sf))
                           * nu_eqII(j)) =E= 0;
                              ^^^ h is uncontrolled
```

**Example (glider):**
```gams
* stat_step is a scalar equation (no domain)
* But references vel(c,h) where h is not in a sum — $149
stat_step.. ... + sum((c,i), ((-1) * ((vel(c,i) + vel(c,h)) * 0.5))
                                                       ^^^ h is uncontrolled
```

**Sub-patterns:**
- **Scalar stationarity equation referencing indexed symbols** (dyncge, glider, ampl): The stationarity variable has no domain but the derivative expression includes free set indices
- **Domain mismatch in stationarity** (harker, korcge, paklive, robert, shale, tabora): The stationarity equation's domain doesn't cover all sets used in the expression

**Fix:** Fix the translator's automatic differentiation and stationarity equation generation to properly handle set domains — either by adding missing domains to the stationarity equation or by recognizing when set indices need to be summed out.

**Estimated Effort:** 3-5h (complex due to interaction with AD engine)

---

### 2.4 Subcategory D: Negative Exponent Needs Parentheses (3 models)

**GAMS Error Code:** $445 (more than one operator in a row)
**Pipeline Stage:** Emitter (expression formatting)
**Models:** launch, ps2_f_eff, ps2_f_inf

**Root Cause:**
The emitter outputs expressions like `x ** -0.9904` which GAMS interprets as two consecutive operators (`**` then `-`). GAMS requires `x ** (-0.9904)` to clarify that the negative sign is part of the exponent.

**Example (launch):**
```gams
* Emitted (invalid):
stat_aweight(s).. 6739.127337 * pweight(s) ** -0.9904 * ...
                                            ^^ ^^^^^^^ $445

* Should be:
stat_aweight(s).. 6739.127337 * pweight(s) ** (-0.9904) * ...
```

**Fix:** In the emitter's expression formatting, wrap negative numeric literals in parentheses when they appear as the RHS of `**` (power operator).

**Estimated Effort:** 1h (simple pattern: detect `** -` in expression output and add parentheses)

---

### 2.5 Subcategory E: Set Index Quoted as String Literal (7 models)

**GAMS Error Code:** $116 (label is unknown)
**Pipeline Stage:** Emitter (identifier quoting)
**Models:** irscge, lrgcge, moncge, quocge, sample, stdcge, twocge

**Root Cause:**
The emitter quotes set indices as string literals (`"J"`) when they should be bare identifiers (`J`). In GAMS, `SAM("TRF",J)` references the set element `J` from the domain, while `SAM("TRF","J")` tries to look up the literal string "J" as a label — which fails because "J" is a set name, not a set element.

**Example (irscge, lrgcge, moncge, quocge, stdcge):**
```gams
* Emitted (invalid):
tm0(j) = SAM("TRF","J");    ← $116: "J" is not a known label
                  ^^^

* Original (valid):
Tm0(j) = SAM("TRF",J);     ← J references set j (uppercase alias)
                  ^
```

**Pattern:** 6 of the 7 models are CGE models (irscge, lrgcge, moncge, quocge, stdcge, twocge) with the identical `SAM("TRF","J")` pattern. The 7th model (sample) has a similar issue with `data(h,"pop")` where `data` is a Table with no data (overlaps with Subcategory A).

**Fix:** Fix the emitter to distinguish between set references (bare identifiers) and string literals (quoted) in parameter indexing. When a parameter index position matches a declared set name, emit it as a bare identifier.

**Estimated Effort:** 1-2h

---

### 2.6 Subcategory F: GAMS Built-in Function Name Collision (1 model)

**GAMS Error Codes:** $121 (set expected), $140 (unknown symbol)
**Pipeline Stage:** Translator (identifier naming)
**Models:** mingamma

**Root Cause:**
The original model uses `gamma` as a variable name, but `gamma` is a GAMS built-in function (the gamma function). The generated MCP uses `gamma(x1)` in stationarity equations, which GAMS interprets as a function call rather than a variable reference.

**Example:**
```gams
* Emitted stationarity equation:
stat_x1.. 0 + ((-1) * (gamma(x1) * psi(x1))) * nu_y1def - piL_x1 =E= 0;
                        ^^^^^^^^^^ $140: GAMS interprets as gamma function call

* Also: psi(x1) — psi is also a GAMS built-in function
```

**Fix:** Add a reserved-word check to the translator/emitter that renames variables colliding with GAMS built-in functions (e.g., `gamma` → `gamma_v`, `psi` → `psi_v`).

**Estimated Effort:** 1h

---

### 2.7 Subcategory G: Set Index Reuse Conflict in Sum (2 models)

**GAMS Error Code:** $125 (set is under control already)
**Pipeline Stage:** Translator (sum domain handling)
**Models:** kand, prolog

**Root Cause:**
The translator generates `sum((nn,n), ...)` where `n` is both the outer assignment index and an inner sum index. GAMS does not allow a set to appear both as a controlling index and inside a nested sum domain.

**Example (kand):**
```gams
* prob(n) = sum((nn,n), stdat(nn,"prob") * stdat(n,"prob"));
*                   ^ $125: n is already controlling the LHS
```

**Fix:** The translator needs to alias conflicting indices — e.g., generate `sum((nn,n__), ...)` with a fresh alias for the inner index.

**Estimated Effort:** 1-2h

---

### 2.8 Subcategory I: MCP Variable Not Referenced in Equations (1 model)

**GAMS Error Code:** $483 (mapped variables have to appear in the model)
**Pipeline Stage:** Translator (MCP model statement)
**Models:** nemhaus

**Root Cause:**
The MCP model statement maps variable `xb` to an equation, but `xb` does not appear in any of the model's equations. GAMS requires that every variable in an MCP pairing must appear in at least one equation.

**Example:**
```gams
Solve mcp_model using MCP;
**** $483 xb no ref to var in equ.var
**** $483 y no ref to var in equ.var
```

**Fix:** Ensure the translator only includes variables in the MCP model statement if they actually appear in the generated equations.

**Estimated Effort:** 1h

---

### 2.9 Subcategory J: Equation-Variable Dimension Mismatch (1 model)

**GAMS Error Code:** $70 (dimensions of the equ.var pair do not conform)
**Pipeline Stage:** Translator (equation-variable pairing)
**Models:** pdi

**Root Cause:**
The MCP model statement pairs an equation with a variable of different dimensionality. GAMS requires that paired equations and variables in MCP have matching dimensions.

**Fix:** Fix the translator's MCP pairing logic to ensure equation and variable dimensions match.

**Estimated Effort:** 1h

---

## 3. Recommended Fix Order

Based on model count, batch-fix potential, and estimated effort:

| Priority | Subcategory | Models | Effort | Rationale |
|----------|-------------|--------|--------|-----------|
| 1 | A: Missing Table data | 16 | 4-6h | Highest leverage: one fix unblocks 16 models |
| 2 | E: Set index quoting | 7 | 1-2h | Simple emitter fix, unblocks 7 CGE models |
| 3 | D: Negative exponent parens | 3 | 1h | Trivial emitter fix, unblocks 3 models |
| 4 | C: Uncontrolled set | 9 | 3-5h | Complex translator fix, but affects 9 models |
| 5 | B: Domain violation | 5 | 2-3h | Emitter data formatting fix |
| 6 | G: Set index reuse | 2 | 1-2h | Translator alias generation |
| 7 | F: Reserved word collision | 1 | 1h | Identifier renaming |
| 8 | I: MCP variable unreferenced | 1 | 1h | Model statement filtering |
| 9 | J: Dimension mismatch | 1 | 1h | Pairing logic fix |

**Recommended Sprint 21 approach (within 8-12h budget):**
1. **Priority 1-3 (E + D + partial A):** Fix set index quoting, negative exponent parenthesization, and begin Table data capture — estimated 6-9h, unblocks 10-26 models
2. **Priority 4 (C) if time permits:** Address uncontrolled set issues — estimated 3-5h additional
3. **Defer to Sprint 22:** Subcategories B, F, G, I, J (10 models total, ~6-8h) — these are lower-leverage individual fixes

---

## 4. Stage Distribution Summary

| Pipeline Stage | Subcategories | Model Count | % of Total |
|---------------|---------------|-------------|-----------|
| Parser (IR builder) | A | 16 | 36% |
| Translator (KKT generation) | C, F, G, I, J | 14 | 31% |
| Emitter (formatting/quoting) | B, D, E | 15 | 33% |

The errors are distributed across all three pipeline stages with no single stage dominating. The parser-stage issue (missing Table data) is the single largest subcategory, but translator and emitter issues together account for 64% of models.

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Fixing Table data parsing exposes secondary errors | High | Low | Models may have additional issues after data is present; re-test after fix |
| Uncontrolled set fix requires AD engine changes | Medium | High | May need to restructure how stationarity equations handle free indices |
| Set index quoting fix causes regressions | Low | Medium | Test against working CGE models to verify quoting logic |
| Multiple overlapping errors in some models | Medium | Low | Some models (egypt, korcge) have errors from multiple subcategories; may need fixes from multiple categories |

---

## 6. Per-Model Error Summary

| Model | Primary Code | Total Errors | Subcategory | First Error |
|-------|-------------|-------------|-------------|-------------|
| agreste | $170 | 13 | B | Domain violation in `labor(p,tm)` data |
| ampl | $149 | 5 | C | Uncontrolled set in `stat_s` equation |
| china | $170 | 25 | B | Domain violation in parameter data |
| dyncge | $149 | 22 | C | Uncontrolled `h` in `stat_epsilon` |
| egypt | $170 | 31 | B | Domain violation in `regwat(r,tm)` data |
| fawley | $170 | 5 | B | Domain violation in parameter data |
| glider | $149 | 210 | C | Uncontrolled `h` in `stat_step` |
| gtm | $170 | 28 | B | Domain violation in parameter data |
| gussrisk | $141 | 6 | A | Missing parameter data |
| harker | $149 | 18 | C | Uncontrolled set in stationarity eqn |
| hydro | $141 | 3 | A | Missing parameter data |
| iobalance | $141 | 4 | A | Table `z1` data not emitted |
| irscge | $116 | 6 | E | `SAM("TRF","J")` — J quoted as string |
| kand | $125 | 3 | G | `sum((nn,n),...)` — n under control |
| korcge | $140 | 12 | C | `e.l(i)` before declaration + $149 |
| launch | $445 | 22 | D | `** -0.9904` needs parentheses |
| least | $66 | 2 | A | Table `dat` data not emitted |
| lmp2 | $141 | 3 | A | Subset `n(nn)` not assigned |
| lrgcge | $116 | 6 | E | `SAM("TRF","J")` — J quoted as string |
| marco | $141 | 3 | A | Missing parameter data |
| markov | $66 | 2 | A | Missing data in equations |
| mine | $66 | 2 | A | Missing data in equations |
| mingamma | $121 | 4 | F | `gamma(x1)` — built-in name collision |
| moncge | $116 | 6 | E | `SAM("TRF","J")` — J quoted as string |
| nemhaus | $483 | 1 | I | `xb`, `y` not referenced in equations |
| otpop | $141 | 3 | A | Missing parameter data |
| paklive | $149 | 52 | C | Uncontrolled set in stationarity eqn |
| paperco | $66 | 2 | A | Missing data in equations |
| pdi | $70 | 3 | J | Equation-variable dimension mismatch |
| prolog | $125 | 8 | G | Set under control in sum domain |
| ps10_s_mn | $141 | 6 | A | Missing parameter data |
| ps2_f_eff | $445 | 3 | D | `** -N` needs parentheses |
| ps2_f_inf | $445 | 3 | D | `** -N` needs parentheses |
| ps5_s_mn | $141 | 6 | A | Missing parameter data |
| qdemo7 | $141 | 4 | A | Parameter `alpha` not assigned |
| quocge | $116 | 6 | E | `SAM("TRF","J")` — J quoted as string |
| robert | $149 | 3 | C | Uncontrolled set in stationarity eqn |
| sample | $116 | 4 | E | Label not found in data reference |
| shale | $149 | 68 | C | Uncontrolled set in stationarity eqn |
| ship | $141 | 3 | A | Missing parameter `hb` data |
| sroute | $141 | 3 | A | Parameter `darc` not assigned |
| stdcge | $116 | 6 | E | `SAM("TRF","J")` — J quoted as string |
| tabora | $149 | 64 | C | Uncontrolled set in stationarity eqn |
| tforss | $66 | 2 | A | Missing data in equations |
| twocge | $116 | 7 | E | `SAM("TRF","J",r)` — J quoted |

---

## 7. Notes

- **GAMS version:** All testing was done with GAMS v53 (`/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams`)
- **Error code $257** appears in most models as a cascading error ("Solve statement not checked because of previous errors") and is excluded from root cause analysis
- **Multi-cause models:** Several models (egypt, korcge, shale) have errors from multiple subcategories. The primary subcategory was determined by the first non-cascading error
- **Table data vs. inline data:** Subcategory A covers missing parameter/Table data, including both `Table` declarations with multi-line data blocks and certain inline or derived parameter assignments. Most A-cases involve `Table` data; inline parameter data (`/key1 val1, key2 val2/`) is usually captured correctly by the IR builder
- **$66 vs $141:** Both indicate missing data. $141 appears when the parameter is used in an assignment; $66 appears at the Solve statement when equations reference parameters with no data
