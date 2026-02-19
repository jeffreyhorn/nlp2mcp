# Lexer Invalid Char Error Catalog — Sprint 20 Update

**Created:** 2026-02-19
**Sprint:** 20 Prep Task 3
**Purpose:** Re-classify all remaining `lexer_invalid_char` failures after Sprint 19 (72 → 27 models)
**Reference:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (original A–K taxonomy)

---

## Executive Summary

**Sprint 19 result:** 72 → 27 models (45 fixed — exceeded the "below 30" target)

**Exact count confirmed:** 27 models still fail with `lexer_invalid_char` (not fewer — no additional silent fixes found)

**Subcategory distribution (Sprint 20 baseline):**

| ID | Subcategory | Count | Grammar-Fixable? | Priority | Est. Effort |
|----|-------------|-------|-----------------|----------|-------------|
| A | Tuple/Compound Set Data Syntax | 6 | Yes | P1 — High ROI | 3–4h |
| B | Cascading Parse Failures | 3 | Indirect | P2 | 0h (resolve by fixing root) |
| D | Lead/Lag Indexing | 2 | Yes | P1 | 0h (will be resolved by planned Sprint 20 IndexOffset `to_gams_string()` work) |
| E | Special Values / Inline Scalar Data | 3 | Yes | P1 | 1–2h |
| F | Declaration/Syntax Gaps | 0 | Yes | P1 | 0h |
| G | Set Element Descriptions | 0 | Yes | P1 — Quick win | 0h |
| H | Control Flow | 2 | Yes | P1 | 1–2h |
| J | Bracket/Brace / Compile-time | 3 | Partial | P2 | 1h (1 grammar; 2 preprocessor) |
| K | Miscellaneous | 1 | Investigate | P3 | 1–2h |
| L | Set-Model Exclusion (`all - x`) | 5 | Yes | P1 — Quick win | 1–2h |
| M | File/Acronym/Unsupported Declarations | 2 | Yes | P1 | 1–2h |
| | **Total** | **27** | | | **~9–15h** |

**Note on Subcategory D:** `mine` and `pindyck` are both now classified as cascading failures of
lead/lag expressions — both will resolve when the Sprint 20 IndexOffset `to_gams_string()` fix
(sparta/tabora/otpop) is applied and the grammar handles `x(t+1)` and `t-1` lag fully.
They are listed as "D" for taxonomy consistency but the fix is already in progress.

**Top-3 highest-ROI subcategories:**
1. **L: Set-Model Exclusion** — 5 models, ~1–2h effort, pure grammar extension (new `all - set` syntax in model statements)
2. **A: Tuple/Compound Set Data** — 6 models, ~3–4h, known fix approach from Sprint 19
3. **B: Cascading** — 3 models, 0h, will resolve when root-cause subcategories (A, D, H) are fixed

**Quick wins (≤2h grammar, ≥2 models):**
- **L: Set-Model Exclusion** — 5 models, `/ all - x /` pattern in Model statements (~1–2h)
- **E: Inline Scalar Data** — 3 models, `scalar / .value /` pattern (~1h, may already work with Sprint 19 fixes)
- **H: Control Flow (`lop` abort$ pattern)** — 1 model (`lop`), `abort$` statement support (~1h) — also unblocks other H models
- **M: File/Acronym declarations** — 2 models, skip or stub unsupported declarations (~1–2h)

---

## What Sprint 19 Fixed

Sprint 19 resolved 45 of the original 72 models. Notable by subcategory:

| Original Subcategory | Fixed Count | Examples |
|---------------------|-------------|---------|
| A (Tuple/Compound Set Data) | 6 | china, egypt, kand, marco, paklive, shale, srkandw |
| B (Cascading) | 11 | agreste, ampl, camcge→partial, fawley, feedtray, gtm, iswnm, korcge, nebrazil, otpop |
| C (Put Statement Format) | 6 | apl1pca, prodsp2, ps10_s, ps10_s_mn, ps5_s_mn, stdcge |
| D (Lead/Lag) | 2 | launch, sparta, tabora → translate success |
| E (Special Values) | 4 | lands, ship, tforss, gussrisk→partial |
| F (Declaration Gaps) | 7 | imsl, qdemo7, robustlp, solveopt, tricp, uimp, wall |
| G (Set Element Descriptions) | 3 | ganges, gangesx, weapons |
| H (Control Flow) | 1 | lmp2 |
| I (Model/Solve Issues) | 5 | mlbeta, mlgamma, pdi, qsambal, sambal |
| J (Bracket/Brace) | 1 | clearlak (preprocessor fix) |

---

## Per-Model Status Table (27 remaining)

| Model | Subcategory | Failing Token | Failing Line Context | Root Pattern | Fix Effort |
|-------|-------------|--------------|---------------------|--------------|------------|
| camcge | L (Set-Model Exclusion) | `-` | `Model camcge / all - caeq /;` | `all - setname` in model statement | Shared fix with L |
| cesam | L (Set-Model Exclusion) | `.` | `Model m_SAMENTROP / d_A.A, d_TSAM.TSAM /` | Dotted model attribute in model list | Shared fix with L |
| cesam2 | E (Inline Scalar Data) | `/` | `stderr1 '...' / .05 /` | Scalar param with leading-decimal value | ~1h |
| dinam | K (Miscellaneous) | `o` | Table header with inline comment text | Table header with non-standard text after dimensions | Investigate |
| fdesign | B (Cascading) | `)` | After `if(t.l > 0, ...)` → cascades to `Model / all /` | Cascading from `if()` statement | Fix root (H: if/loop) |
| ferts | L (Set-Model Exclusion) | `-` | `stat2 / all - mbd /` | `all - setname` in set expression | Shared fix with L |
| gussrisk | E (Inline Scalar Data) | `/` | `funds '...' / 500 /` | Scalar param inline data | ~1h |
| indus | A (Compound Set Data) | `(` | `wheat.bullock.la-plant.(standard,light,heavy,january)` | Tuple with parenthesized sub-list | Extend A fix |
| iobalance | H (Control Flow) | `o` | `repeat … oldr(i) = r(i);` | `repeat/until` loop body | ~1h |
| lop | H (Control Flow) | `S` | `abort$card(error02) error02; Set ll(s,s)...` | `abort$` statement causes cascading | ~1h |
| mathopt3 | J (Bracket/Brace) | `+` | `10*sqr(sin[x5 - x6 + x1])` | Square bracket function call in expression | ~1h |
| mexls | A (Compound Set Data) | `r` | `wire rod 'rolling...'` | Multi-word (space-containing) set element | Extend A fix |
| mine | D (Lead/Lag) | `x` | `x.up(l,i,j)` cascades from `pr(k,l+1,i,j)..` | Cascading from `l+1` lead/lag in equation | Sprint 20 IndexOffset fix |
| nemhaus | B (Cascading) | `j` | `j(jj) = yes;` inside `loop(jj$more, ...)` | Cascading from `loop` with `$` condition | Fix root (H) |
| nonsharp | B (Cascading) | `i` | `iter = iter + 1` | Cascading from complex expression | Fix root (F/K) |
| paperco | A (Compound Set Data) | `c` | `(ground \n chips )  40  55` | Multi-line table row label with continuation | Extend A fix |
| pindyck | D (Lead/Lag) | `d` | `display td.l` cascades from `r.l(t-1)` | Cascading from `t-1` lag in loop | Sprint 20 IndexOffset fix |
| saras | J (Bracket/Brace) | `]` | `* [Stripped: $offText]` | Preprocessor stripping artifact leaves `]` | Preprocessor fix |
| sarf | A (Compound Set Data) | `(` | `sugar-beet.spray.(sch-1*sch-3)` | Tuple with parenthesized range | Extend A fix |
| senstran | M (Unsupported Declaration) | `'` | `File repdat 'sensitivity data report file';` | `File` declaration not supported | ~1h |
| spatequ | L (Set-Model Exclusion) | `.` | `P2R3_MCP / DEM, SUP, IN_OUT.P, DOM_TRAD.X /;` | Dotted variable.attr in model list | Shared fix with L |
| springchain | J (Bracket/Brace) | `[` | `L0 "rest length" / [2*sqrt(...)] /` | Square bracket expression in scalar data | Preprocessor/$eval |
| tfordy | L (Set-Model Exclusion) | `-` | `antala 'case a' / all - sy2 - sy3 /` | `all - setname` in set definition | Shared fix with L |
| trnspwl | E (Inline Scalar Data) | `/` | `xlow / 50 /` | Scalar param inline data (no quotes) | Shared fix with E |
| turkey | A (Compound Set Data) | `s` | `(chickpea,drybean,lentil)` in table header | Parenthesized element group in table column header | Extend A fix |
| turkpow | A (Compound Set Data) | `.` | `hydro-4.1978` in parameter data | Compound element with numeric suffix | Extend A fix |
| worst | M (Unsupported Declaration) | `-` | Cascades from `Acronym future, call, puto;` | `Acronym` declaration not supported | ~1h |

---

## Per-Subcategory Summary

| Subcategory | Name | Count | Models | Fix Effort | Notes |
|-------------|------|-------|--------|------------|-------|
| A | Compound Set Data | 6 | indus, mexls, paperco, sarf, turkey, turkpow | 3–4h | Extends Sprint 19 A fix; new patterns: multi-word elements, parenthesized sub-lists, ranges |
| B | Cascading Failures | 3 | fdesign, nemhaus, nonsharp | 0h | Fix root cause (D, H, F/K) |
| D | Lead/Lag Indexing | 2 | mine, pindyck | 0h (Sprint 20) | Will resolve with planned IndexOffset `to_gams_string()` fix |
| E | Inline Scalar Data | 3 | cesam2, gussrisk, trnspwl | ~1h | Scalar param `/ value /` missing; may be grammar gap or whitespace issue |
| F | Declaration Gaps | 0 | — | — | All Sprint 19 F models fixed |
| G | Set Element Descriptions | 0 | — | — | All Sprint 19 G models fixed (ganges, gangesx, weapons) |
| H | Control Flow | 2 | iobalance, lop | 1–2h | `repeat/until` + `abort$` — both blocked earlier H models too |
| J | Bracket/Brace | 3 | mathopt3, saras, springchain | 1h grammar (mathopt3); 2 preprocessor | saras: preprocessor artifact; springchain: `$eval`/compile-time |
| K | Miscellaneous | 1 | dinam | 1–2h | Table header with inline comment — unique pattern |
| L | Set-Model Exclusion | 5 | camcge, cesam, ferts, spatequ, tfordy | 1–2h | NEW subcategory: `/ all - setname /` and `/ model.attr /` patterns in Model/Set statements |
| M | File/Acronym Decls | 2 | senstran, worst | 1–2h | NEW subcategory: unsupported `File` and `Acronym` declaration keywords |

---

## New Subcategories Identified

### Subcategory L: Set-Model Exclusion (`all - setname`)

**Pattern:** GAMS allows `/ all - subset /` in set definitions and `Model m / all - eqname /` in model statements to exclude elements. The grammar doesn't handle `all` as a special keyword in these contexts.

**Models:** camcge, ferts, tfordy (set exclusion); spatequ, cesam (model statement with dotted `eq.var` form)

**Failing examples:**
```gams
Model camcge / all - caeq /;       (* camcge: 'all - eqname' in model list *)
antala / all - sy2 - sy3 - sy4 /;  (* tfordy: 'all - setname' in set definition *)
stat2 / all - mbd /                (* ferts: 'all - setname' in set expression *)
P2R3_MCP / DEM, SUP, IN_OUT.P /;   (* spatequ: 'eq.var' form in model list *)
```

**Fix approach:** Add `all_except` rule: `"all" ("-" ID)+` in set/model data contexts. Also extend model statement to accept `eq_name "." var_name` (complementarity pair form).

**Estimated effort:** 1–2h

**ROI:** High — 4–5 models, clean grammar extension, low risk.

---

### Subcategory M: Unsupported Declaration Keywords

**Pattern:** Models use `File` and `Acronym` GAMS declarations not yet implemented in the grammar.

**Models:** senstran (`File`), worst (`Acronym`)

**Failing examples:**
```gams
File repdat 'sensitivity data report file';   (* senstran *)
Acronym future, call, puto;                   (* worst *)
```

**Fix approach:**
- `File`: Add `file_decl: "File" ID ("'" text "'" )? ";"` — stub the file handle (no IR needed for MCP translation)
- `Acronym`: Add `acronym_decl: "Acronym" ID ("," ID)* ";"` — treat as set/type declaration, can be ignored in IR

**Estimated effort:** 1–2h

---

## Top-3 Highest-ROI Subcategories

### 1. Subcategory L: Set-Model Exclusion — 5 models, ~1–2h
**Why:** Single consistent pattern (`all - x`), pure grammar addition, no IR/AD changes needed, unblocks camcge (CGE model), cesam, ferts, tfordy, spatequ.

### 2. Subcategory A: Compound Set Data — 6 models, ~3–4h
**Why:** Sprint 19 already implemented the core dotted-element fix; Sprint 20 needs to extend to handle parenthesized sub-lists `(sch-1*sch-3)`, multi-word elements (`wire rod`), and hyphenated-with-numeric-suffix elements (`hydro-4.1978`). The fix framework is already in place.

### 3. Subcategory B: Cascading — 3 models, ~0h
**Why:** These models (fdesign, nemhaus, nonsharp) will resolve for free when subcategories D (IndexOffset) and H (control flow) are fixed. Zero additional effort required.

---

## Quick Wins

### Quick Win 1: Subcategory L — `all - setname` in set/model statements (~1–2h, 5 models)
Grammar addition: recognize `all` as keyword and `all - name` pattern.
```
model_element: ID ("." ID)?
             | "all" ("-" ID)*
```

### Quick Win 2: Subcategory M — `File` and `Acronym` declarations (~1–2h, 2 models)
Grammar stubs for two unsupported declaration types that can be safely ignored in IR.

### Quick Win 3: Subcategory H — `repeat/until` and `abort$` (~1–2h, 2 models)
The `iobalance` fix (repeat/until) also unblocks cascading models (nemhaus from B).
The `abort$` fix (lop) unblocks a set declaration.

---

## Subcategory D / IndexOffset Overlap Assessment

**Unknown 4.4 answer:** The 2 remaining Subcategory D models (`mine`, `pindyck`) are cascading failures:
- `mine`: Equation `pr(k,l+1,i,j)..` uses `l+1` lead/lag; the parser fails on this, then cascades to `x.up(l,i,j)` 
- `pindyck`: Loop `loop(t$to(t), r.l(t) = r.l(t-1)-d.l(t))` uses `t-1` lag; cascades to `display` statement

Both will be resolved when the Sprint 20 IndexOffset `to_gams_string()` fix completes — the grammar already supports `offset_paren`/`offset_func` from Sprint 19 PRs #785. These do **not** need separate grammar work.

---

## Silent Fixes from Sprint 19

Comparing Sprint 19 catalog (72) to current count (27): **45 models fixed**.

Notable unexpected fixes (models that weren't in the primary Sprint 19 targets but got fixed):
- `launch`, `mine`, `sparta`, `tabora` — originally Subcategory D (lead/lag), now translate successfully (launch, sparta, tabora) or are only cascading parse failures (mine)
- `camcge` — originally B (cascading from prod), now fails on a new pattern (L: model exclusion), suggesting its original cascading root was fixed but a new syntax gap exposed
- `clearlak` — originally J (preprocessor), apparently fixed
- All 5 Subcategory I models (mlbeta, mlgamma, pdi, qsambal, sambal) — fixed

**Zero new models** entered the `lexer_invalid_char` category (no regression). The 27 remaining are a strict subset of the original 72.

---

## Sprint 20 Implementation Order (Recommended)

### Phase 1: Quick wins (~3–5h, ~9 models + cascading)
| Priority | Subcategory | Models | Effort |
|----------|-------------|--------|--------|
| 1 | L: Set-Model Exclusion | camcge, cesam, ferts, tfordy, spatequ | 1–2h |
| 2 | M: File/Acronym Decls | senstran, worst | 1–2h |
| 3 | H: Control Flow | iobalance, lop | 1–2h |
| — | B: Cascading (free) | nemhaus → resolves | 0h |

### Phase 2: Core grammar (~4–6h, ~8 models)
| Priority | Subcategory | Models | Effort |
|----------|-------------|--------|--------|
| 4 | A: Compound Set Data (extended) | indus, mexls, paperco, sarf, turkey, turkpow | 3–4h |
| 5 | E: Inline Scalar Data | cesam2, gussrisk, trnspwl | 1h |

### Phase 3: If time permits (~2–4h, ~4 models)
| Priority | Subcategory | Models | Effort |
|----------|-------------|--------|--------|
| 6 | J: mathopt3 (bracket) | mathopt3 | 1h |
| 7 | K: Miscellaneous | dinam | 1–2h |
| 8 | J: preprocessor | saras, springchain | ~2h (preprocessor scope) |

### Automatic (via IndexOffset Sprint 20 work)
| Model | Resolution |
|-------|-----------|
| mine | Resolves when IndexOffset `to_gams_string()` extended |
| pindyck | Resolves when IndexOffset `to_gams_string()` extended |
| fdesign | Resolves when H (if/loop) is fixed |
| nonsharp | Resolves when F/K root cause fixed |

---

## Appendix: Complete 27-Model List

| # | Model | Subcategory | Failing Token | Grammar-Fixable? |
|---|-------|-------------|--------------|-----------------|
| 1 | camcge | L (Set-Model Exclusion) | `-` | Yes |
| 2 | cesam | L (Set-Model Exclusion) | `.` | Yes |
| 3 | cesam2 | E (Inline Scalar Data) | `/` | Yes |
| 4 | dinam | K (Miscellaneous) | `o` | Investigate |
| 5 | fdesign | B (Cascading → H) | `)` | Indirect |
| 6 | ferts | L (Set-Model Exclusion) | `-` | Yes |
| 7 | gussrisk | E (Inline Scalar Data) | `/` | Yes |
| 8 | indus | A (Compound Set Data) | `(` | Yes |
| 9 | iobalance | H (Control Flow) | `o` | Yes |
| 10 | lop | H (Control Flow) | `S` | Yes |
| 11 | mathopt3 | J (Bracket/Brace) | `+` | Yes |
| 12 | mexls | A (Compound Set Data) | `r` | Yes |
| 13 | mine | D (Lead/Lag → IndexOffset) | `x` | Indirect (Sprint 20) |
| 14 | nemhaus | B (Cascading → H) | `j` | Indirect |
| 15 | nonsharp | B (Cascading → F/K) | `i` | Indirect |
| 16 | paperco | A (Compound Set Data) | `c` | Yes |
| 17 | pindyck | D (Lead/Lag → IndexOffset) | `d` | Indirect (Sprint 20) |
| 18 | saras | J (Bracket/Brace) | `]` | No (preprocessor) |
| 19 | sarf | A (Compound Set Data) | `(` | Yes |
| 20 | senstran | M (Unsupported Decl) | `'` | Yes |
| 21 | spatequ | L (Set-Model Exclusion) | `.` | Yes |
| 22 | springchain | J (Bracket/Brace) | `[` | No (preprocessor/$eval) |
| 23 | tfordy | L (Set-Model Exclusion) | `-` | Yes |
| 24 | trnspwl | E (Inline Scalar Data) | `/` | Yes |
| 25 | turkey | A (Compound Set Data) | `s` | Yes |
| 26 | turkpow | A (Compound Set Data) | `.` | Yes |
| 27 | worst | M (Unsupported Decl) | `-` | Yes |
