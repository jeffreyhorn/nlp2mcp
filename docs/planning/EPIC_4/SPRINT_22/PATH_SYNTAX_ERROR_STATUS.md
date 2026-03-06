# path_syntax_error Status Update (Sprint 22 Prep Task 2)

**Created:** 2026-03-05
**Sprint:** 22 (Prep Task 2)
**Status:** Complete — ready for Sprint 22 fix design (Task 7)
**Data Source:** `data/gamslib/gamslib_status.json` (updated_date=2026-02-12, GAMS 51.3.0; Sprint 21 Day 12 pipeline run)

---

## 1. Executive Summary

The path_syntax_error category currently contains **43 models** (down from the Sprint 21 baseline of 48, of which 45 were classified in the catalog). Sprint 21 fixes moved 22 models out of this category, while 17 newly-translating models entered it. The net change is −5.

Sprint 22 targets path_syntax_error **≤ 30** (−13 models). Analysis shows this is achievable by fixing **Subcategory A** (15 models, highest leverage) alone. Fixing A + C (25 models total) would far exceed the target.

### Key Changes from Sprint 21

| Subcategory | Sprint 21 | Current | Delta | Notes |
|-------------|-----------|---------|-------|-------|
| A: Missing data | 16 | 15 | −1 | 9 resolved, 8 new, 2 reclassified in, 2 reclassified out |
| B: Domain violation | 5 | 2 | −3 | 2 resolved, 3 reclassified out, 2 new |
| C: Uncontrolled set | 9 | 10 | +1 | 1 new (trnspwl) |
| D: Negative exponent | 3 | 0 | −3 | **FULLY RESOLVED** |
| E: Set quoting | 7 | 0 | −7 | **FULLY RESOLVED** |
| F: Built-in name collision | 1 | 1 | 0 | |
| G: Set index reuse | 2 | 4 | +2 | 2 new |
| I: Unreferenced var | 1 | 2 | +1 | 1 new |
| J: Dimension mismatch | 1 | 2 | +1 | launch reclassified from D |
| K: smax domain (NEW) | — | 1 | +1 | tricp (was unsubcategorized) |
| New patterns | — | 5 | +5 | GUSS, duplicate element, hyphenated labels, etc. |
| Pipeline artifact | — | 1 | +1 | feedtray: MCP file missing |
| Unsubcategorized | 3 | 0 | −3 | Legacy bucket emptied (all mapped to New patterns or Pipeline artifact) |
| **Total** | **48** | **43** | **−5** | |

### What Sprint 21 Fixed

- **Subcategory D** (3 models): Negative exponent parenthesization — **fully resolved**
- **Subcategory E** (7 models): Set index quoting — **fully resolved**
- **Subcategory A partial** (7 models): Table data capture, emission ordering improvements
- **Plus:** egypt (B→translate timeout), fawley (B→path_solve_terminated), sroute (A→path_solve_license)

---

## 2. Model Movement Analysis

### 2.1 Models Moved OUT of path_syntax_error (22 models)

| Model | Sprint 21 Subcat | New Status | How |
|-------|------------------|------------|-----|
| dinam | unsubcategorized | translate_failure (timeout) | Regressed to translation timeout |
| egypt | B ($170) | translate_failure (timeout) | Regressed to translation timeout |
| fawley | B ($170) | path_solve_terminated | Syntax fixed but solve terminated |
| ferts | unsubcategorized | translate_failure (timeout) | Regressed to translation timeout |
| hydro | A ($141) | model_optimal | Table data / emission fix |
| iobalance | A ($141) | model_infeasible | Syntax fixed but model infeasible |
| irscge | E ($116) | model_optimal | Set quoting fix |
| least | A ($66) | model_optimal | Data emission fix |
| lrgcge | E ($116) | model_optimal | Set quoting fix |
| mine | A ($66) | model_optimal | Data emission fix |
| moncge | E ($116) | model_optimal | Set quoting fix |
| otpop | A ($141) | path_solve_terminated | Syntax fixed but solve terminated |
| ps2_f_eff | D ($445) | model_optimal | Negative exponent fix |
| ps2_f_inf | D ($445) | model_optimal | Negative exponent fix |
| qdemo7 | A ($141) | model_optimal | Data emission fix |
| quocge | E ($116) | model_optimal | Set quoting fix |
| sample | E ($116) | model_optimal | Set quoting fix |
| ship | A ($141) | model_optimal | Data emission fix |
| sroute | A ($141) | path_solve_license | Syntax fixed but license limit |
| stdcge | E ($116) | model_optimal | Set quoting fix |
| tforss | A ($66) | path_solve_terminated | Syntax fixed but solve terminated |
| twocge | E ($116) | model_infeasible | Set quoting fixed but model infeasible |

**New status distribution:** 13 model_optimal, 3 translate_failure, 3 path_solve_terminated, 2 model_infeasible, 1 path_solve_license

### 2.2 Models Moved IN to path_syntax_error (17 new models)

These models were not in the Sprint 21 catalog — they are newly translating and reaching the solve stage for the first time:

| Model | Error Code | Subcategory | First Error |
|-------|-----------|-------------|-------------|
| camcge | $141 | A | Missing parameter data |
| camshape | $141 | A | Missing parameter data |
| cesam | $170 | B | Domain violation in parameter data |
| cesam2 | $170 | B | Domain violation in parameter data |
| decomp | $66 | A | Missing data in equations |
| feedtray | unknown | Pipeline artifact | MCP file not on disk; JSON records path_syntax_error |
| imsl | $116 | New pattern | Label unknown — needs investigation |
| indus | $141 | A | Missing parameter data |
| nonsharp | $187 | New pattern | Assigned set used as domain |
| qsambal | $141 | A | Missing parameter data |
| ramsey | $141 | A | Missing parameter data |
| sambal | $141 | A | Missing parameter data |
| saras | $140 | A | Unknown symbols — missing parameter/Table data |
| spatequ | $125 | G | Set index reuse conflict |
| srkandw | $125 | G | Set index reuse conflict |
| trnspwl | $149 | C | Uncontrolled set in stationarity |
| worst | $483 | I | MCP variable not referenced |

### 2.3 Models That Stayed in path_syntax_error (26 models)

| Model | Sprint 21 Subcat | Current Subcat | Notes |
|-------|------------------|----------------|-------|
| agreste | B ($170) | **A ($66)** | RECLASSIFIED — now $66 (param 'a' unassigned) |
| ampl | C ($149) | C ($149) | Unchanged |
| china | B ($170) | **A ($141)** | RECLASSIFIED — now $141 (param 'sys' unassigned) |
| dyncge | C ($149) | C ($149) | Unchanged |
| glider | C ($149) | C ($149) | Unchanged |
| gtm | B ($170) | **New pattern ($120/$340)** | RECLASSIFIED — unquoted hyphenated labels |
| gussrisk | A ($141) | **New pattern ($161)** | RECLASSIFIED — GUSS dict syntax |
| harker | C ($149) | C ($149) | Unchanged |
| kand | G ($125) | G ($125) | Unchanged |
| korcge | C ($149) | C ($149) | Unchanged |
| launch | D ($445) | **J ($70)** | RECLASSIFIED — MCP equ/var dimension mismatch |
| lmp2 | A ($141) | A ($141) | Unchanged |
| marco | A ($141) | **New pattern ($172)** | RECLASSIFIED — duplicate element in data block |
| markov | A ($66) | A ($66) | Unchanged — param 'pi' unassigned |
| mingamma | F ($121) | F ($121) | Unchanged |
| nemhaus | I ($483) | I ($483) | Unchanged |
| paklive | C ($149) | C ($149) | Unchanged |
| paperco | A ($66) | A ($66) | Unchanged |
| pdi | J ($70) | J ($70) | Unchanged |
| prolog | G ($125) | G ($125) | Unchanged |
| ps10_s_mn | A ($141) | A ($141) | Unchanged |
| ps5_s_mn | A ($141) | A ($141) | Unchanged |
| robert | C ($149) | C ($149) | Unchanged |
| shale | C ($149) | C ($149) | Unchanged |
| tabora | C ($149) | C ($149) | Unchanged |
| tricp | unsubcategorized | K ($148) | Classified into new Subcategory K |

**Reclassifications:** 6 models changed subcategory. Sprint 21 fixes changed the compilation context, unmasking different underlying errors (agreste, china, launch) or revealing new patterns (gussrisk, marco, gtm).

---

## 3. Current Subcategory Breakdown (43 models)

### 3.1 Subcategory A: Missing Parameter/Table Data (15 models)

**GAMS Error Codes:** $141, $66, $140
**Pipeline Stage:** Parser (IR builder) / Emitter (data emission)

**Stayed (5):** lmp2, markov, paperco, ps10_s_mn, ps5_s_mn
**Reclassified in (2):** agreste (was B), china (was B)
**New (8):** camcge, camshape, decomp, indus, qsambal, ramsey, sambal, saras

**Root Cause:** The IR builder does not capture Table data blocks into `ParameterDef.values`, and some computed parameters are emitted before their data sources. GAMS raises $141/$66/$140 when the empty parameters are referenced.

**Sprint 22 Fix:** Continue Table data capture improvements. Highest-leverage subcategory.

**Estimated Effort:** 4-6h

---

### 3.2 Subcategory B: Domain Violation in Emitted Parameter Data (2 models)

**GAMS Error Code:** $170
**Pipeline Stage:** Emitter (data formatting)

**New (2):** cesam, cesam2

**Note:** All 5 original Sprint 21 Subcategory B models changed status: egypt/fawley moved out; agreste/china reclassified to A; gtm reclassified to new pattern. Current B models are entirely new.

**Sprint 22 Fix:** Emitter domain filtering (adapt Sprint 21 egypt/fawley approach).

**Estimated Effort:** 1-2h

---

### 3.3 Subcategory C: Uncontrolled Set in Stationarity Equations (10 models)

**GAMS Error Code:** $149
**Pipeline Stage:** Translator (KKT generation)

**Stayed (9):** ampl, dyncge, glider, harker, korcge, paklive, robert, shale, tabora
**New (1):** trnspwl

**KU-01 Verification:** CONFIRMED with 2 sub-patterns:
1. **Scalar stationarity with indexed symbols** (ampl, dyncge, glider): Stationarity variable has no domain but derivative includes free set indices
2. **Domain mismatch in stationarity** (harker, korcge, paklive, robert, shale, tabora, trnspwl): Stationarity equation domain doesn't cover all expression sets

Both share the same root cause in KKT assembly — stationarity equations don't properly propagate domain requirements.

**Sprint 22 Fix:** Fix KKT stationarity generator domain propagation.

**Estimated Effort:** 3-5h

---

### 3.4 Subcategory F: GAMS Built-in Function Name Collision (1 model)

**GAMS Error Codes:** $121, $140
**Pipeline Stage:** Translator (identifier naming)
**Models:** mingamma

**KU-16 Verification:** NON-ISSUE for other models. Only mingamma has the collision because stationarity equations use `gamma(x1)` where GAMS interprets it as a function call.

**Estimated Effort:** 1h

---

### 3.5 Subcategory G: Set Index Reuse Conflict in Sum (4 models)

**GAMS Error Code:** $125
**Pipeline Stage:** Translator (sum domain handling)

**Stayed (2):** kand, prolog
**New (2):** spatequ, srkandw

**Sprint 22 Fix:** Generate alias indices for conflicting sum domains.

**Estimated Effort:** 1-2h

---

### 3.6 Subcategory I: MCP Variable Not Referenced in Equations (2 models)

**GAMS Error Code:** $483
**Pipeline Stage:** Translator (MCP model statement)

**Stayed (1):** nemhaus
**New (1):** worst

**KU-17 Verification:** nemhaus is MINLP (binary variables) — cannot participate in MCP. Not just a filtering bug; fundamentally a model-type issue.

**Sprint 22 Fix:** Filter unreferenced variables from MCP model statement. Consider MINLP detection warning.

**Estimated Effort:** 1h

---

### 3.7 Subcategory J: Equation-Variable Dimension Mismatch (2 models)

**GAMS Error Code:** $70
**Pipeline Stage:** Translator (equation-variable pairing)

**Stayed (1):** pdi (16 $70 errors — systematic dimension tracking bug)
**Reclassified in (1):** launch (was D/$445 in Sprint 21; now $70 after neg-exponent fix resolved the $445 errors, unmasking the underlying $70 dimension mismatch)

**KU-18 Verification:** CONFIRMED — systematic dimension tracking bug in MCP translator's equation-variable pairing.

**Sprint 22 Fix:** Fix MCP pair generation dimension matching.

**Estimated Effort:** 1-2h

---

### 3.8 Subcategory K (NEW): smax/sum Domain Tuple Mismatch (1 model)

**GAMS Error Code:** $148
**Pipeline Stage:** Translator (aggregation domain handling)
**Models:** tricp

**Root Cause:** smax/sum expressions have domain tuple with different dimension than the aggregated symbol.

**Sprint 22 Fix:** Fix dimension matching in aggregation domain handling.

**Estimated Effort:** 1h

---

### 3.9 New Patterns Not Matching Existing Subcategories (5 models)

These models have error patterns not seen in the Sprint 21 catalog:

| Model | Error Code | Pattern | Root Cause | Est. Effort |
|-------|-----------|---------|------------|-------------|
| gussrisk | $161 | GUSS dict syntax | Emitter generates GUSS `.param.`/`.level.` syntax that GAMS rejects | 1-2h |
| marco | $172 | Duplicate element | Emitter outputs duplicate data entries for same key | 1h |
| gtm | $120/$340 | Unquoted hyphenated labels | Emitter outputs `d.l(n-central)` instead of `d.l("n-central")` | 1h |
| nonsharp | $187 | Assigned set as domain | Dynamic set used as domain (GAMS requires static declared sets) | 1-2h |
| imsl | $116 | Label unknown | Needs further investigation — possibly data issue or quoting | 1h |

**Note:** gussrisk was previously Subcategory A ($141) and marco was previously Subcategory A ($141). Sprint 21 fixes resolved their original $141 errors, revealing different underlying issues.

### 3.10 Pipeline Artifact Issue (1 model)

| Model | Status | Notes |
|-------|--------|-------|
| feedtray | MCP file missing | JSON records path_syntax_error but MCP file not on disk. Needs pipeline re-run to regenerate or investigate why translation succeeded without producing output. Not actionable until MCP file is available. |

---

## 4. Prioritized Fix Order for Sprint 22

Sprint 22 target: path_syntax_error **≤ 30** (need to fix **≥ 13** models from 43)

| Priority | Subcategory | Models | Effort | Cumulative Fixed | Rationale |
|----------|-------------|--------|--------|-----------------|-----------|
| 1 | A: Missing data | 15 | 4-6h | 15 | Highest leverage: 1 fix type unblocks 15 models |
| 2 | C: Uncontrolled set | 10 | 3-5h | 25 | Second highest: KKT assembly fix for 10 models |
| 3 | G: Set index reuse | 4 | 1-2h | 29 | Quick fix, doubled since Sprint 21 |
| 4 | B: Domain violation | 2 | 1-2h | 31 | Pattern already addressed in Sprint 21 |
| 5 | J: Dimension mismatch | 2 | 1-2h | 33 | Systematic translator fix |
| 6 | I: Unreferenced var | 2 | 1h | 35 | Simple model statement filtering |
| 7 | F: Built-in name collision | 1 | 1h | 36 | Isolated single-model fix |
| 8 | K: smax domain | 1 | 1h | 37 | Single model, new subcategory |
| 9 | New patterns | 5 | 4-7h | 42 | Assorted emitter fixes |

**Note:** feedtray (1 model) excluded from fix plan — MCP file missing, not actionable until pipeline re-run.

**Total estimated effort: 17-27h**

### Recommended Sprint 22 Approach

**Minimum viable (−13 models, hitting ≤30 target):**
- Fix Subcategory A (15 models, 4-6h) — alone exceeds the −13 target

**Recommended scope (−29+ models):**
1. Subcategory A: Missing data (15 models, 4-6h)
2. Subcategory C: Uncontrolled set (10 models, 3-5h)
3. Subcategory G: Set index reuse (4 models, 1-2h)

This would reduce path_syntax_error from 43 to **~14 models** (~29 fixed). Total effort: ~8-13h.

**Stretch goal (−33+ models):**
Add B + J + I + F (7 models, ~4-5h) to reach **~6 models** remaining.

---

## 5. KU Verification Summary

| KU | Status | Finding |
|----|--------|---------|
| KU-01 | **CONFIRMED** | Subcategory C has 2 sub-patterns but same root cause (KKT assembly domain propagation) |
| KU-03 | **REFUTED** | Original Subcategory B models do NOT share a common bug. agreste→$66 (A), china→$141 (A), gtm→$120 (new pattern). Only egypt/fawley were true $170 — both moved out. Current B (cesam, cesam2) are new. |
| KU-16 | **NON-ISSUE** | gamma/psi as parameter names handled context-sensitively by GAMS. Only mingamma has the collision. Fix is isolated. |
| KU-17 | **UPDATED** | nemhaus is MINLP (binary variables) — MCP incompatible model type. Not just a filtering bug. |
| KU-18 | **CONFIRMED** | pdi has 16 systematic $70 errors. launch also has $70 errors (reclassified from D). Systematic dimension tracking bug. |
| KU-19 | **PARTIALLY REFUTED** | tricp needs new Subcategory K ($148). dinam and ferts moved to translate_failure (timeout), not path_syntax_error. |

---

## 6. Per-Model Error Summary (All 43 Current Models)

| Model | Error Code | Errors | Subcategory | Movement | First Error |
|-------|-----------|--------|-------------|----------|-------------|
| agreste | $66 | 2 | A | Reclassified (was B) | Param 'a' unassigned |
| ampl | $149 | 5 | C | Stayed | Uncontrolled set in stationarity |
| camcge | $141 | — | A | New | Missing parameter data |
| camshape | $141 | — | A | New | Missing parameter data |
| cesam | $170 | — | B | New | Domain violation |
| cesam2 | $170 | — | B | New | Domain violation |
| china | $141 | 3 | A | Reclassified (was B) | Param 'sys' unassigned |
| decomp | $66 | — | A | New | Missing data in equations |
| dyncge | $149 | 22 | C | Stayed | Uncontrolled set |
| feedtray | — | — | Pipeline artifact | New | MCP file not on disk |
| glider | $149 | 210 | C | Stayed | Uncontrolled set |
| gtm | $120/$340 | 8 | New pattern | Reclassified (was B) | Unquoted hyphenated labels |
| gussrisk | $161 | 6 | New pattern | Reclassified (was A) | GUSS dict syntax |
| harker | $149 | 18 | C | Stayed | Uncontrolled set |
| imsl | $116 | — | New pattern | New | Label unknown |
| indus | $141 | — | A | New | Missing parameter data |
| kand | $125 | 3 | G | Stayed | Set index reuse |
| korcge | $149 | 12 | C | Stayed | Uncontrolled set |
| launch | $70 | 2 | J | Reclassified (was D) | MCP equ/var dimension mismatch |
| lmp2 | $141 | 3 | A | Stayed | Subset not assigned |
| marco | $172 | 3 | New pattern | Reclassified (was A) | Duplicate element in data |
| markov | $66 | 2 | A | Stayed | Param 'pi' unassigned |
| mingamma | $121 | 4 | F | Stayed | Built-in name collision |
| nemhaus | $483 | 1 | I | Stayed | MINLP binary vars unreferenced |
| nonsharp | $187 | — | New pattern | New | Assigned set as domain |
| paklive | $149 | 52 | C | Stayed | Uncontrolled set |
| paperco | $66 | 2 | A | Stayed | Missing data |
| pdi | $70 | 16 | J | Stayed | Dimension mismatch |
| prolog | $125 | 8 | G | Stayed | Set index reuse |
| ps10_s_mn | $141 | 6 | A | Stayed | Missing parameter data |
| ps5_s_mn | $141 | 6 | A | Stayed | Missing parameter data |
| qsambal | $141 | — | A | New | Missing parameter data |
| ramsey | $141 | — | A | New | Missing parameter data |
| robert | $149 | 3 | C | Stayed | Uncontrolled set |
| sambal | $141 | — | A | New | Missing parameter data |
| saras | $140 | — | A | New | Unknown symbols / missing data |
| shale | $149 | 68 | C | Stayed | Uncontrolled set |
| spatequ | $125 | — | G | New | Set index reuse |
| srkandw | $125 | — | G | New | Set index reuse |
| tabora | $149 | 64 | C | Stayed | Uncontrolled set |
| tricp | $148 | — | K | Stayed (classified) | smax domain tuple mismatch |
| trnspwl | $149 | — | C | New | Uncontrolled set |
| worst | $483 | — | I | New | MCP variable unreferenced |

**Note:** qdemo7 previously belonged to this category but moved out to model_optimal in Sprint 21 and is not included in the 43 current models above.

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Subcategory A fixes expose secondary errors | High | Low | Models may shift to model_infeasible or path_solve_terminated (KU-24) |
| Subcategory C fix breaks currently-solving models | Medium | High | Full regression after fix (KU-02) |
| New models continue entering path_syntax_error | Low | Low | Sprint 22 parse/translate improvements may add 2-5 more |
| Effort estimates too optimistic for Subcat C | Medium | Medium | 3-5h may grow if AD engine changes needed |
| New patterns (GUSS, duplicate, etc.) harder than expected | Medium | Low | Only 5 new-pattern models (excluding feedtray pipeline artifact); can defer to Sprint 23 |
| feedtray MCP file issue blocks classification | Low | Low | Re-run pipeline to regenerate; or skip |

---

## 8. Notes

- **GAMS version:** Pipeline data from `gamslib_status.json` uses GAMS 51.3.0. Manual error classification (GAMS compilation of MCP files) used GAMS v53 (`/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams`). Error codes are consistent across both versions.
- **Subcategory H:** No Subcategory H was ever defined (historical gap from Sprint 21)
- **Subcategories D and E:** Fully resolved in Sprint 21. No models remain.
- **dinam, egypt, ferts:** Were in Sprint 21 unsubcategorized note. All three moved to translate_failure (timeout) — not path_syntax_error. Their Sprint 21 path_syntax_error status was from an earlier pipeline run.
- **Reclassification pattern:** Sprint 21 fixes often resolved the primary error, revealing a different secondary error. This happened to 6 models (agreste, china, gtm, gussrisk, launch, marco). The lesson: fixing one error category may shift models rather than resolve them.

---

**Document Created:** 2026-03-05
**Next Steps:** Use this catalog for Task 7 (Fix Design) and Task 10 (Sprint 22 Detailed Schedule)
