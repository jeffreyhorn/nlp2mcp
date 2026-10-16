# Correctness-Track Pre-Traces — turkpow Class A, the Diagonal Defect, the Structural Sites (Sprint 40 Prep Task 10)

**Measured at:** `b85afbc0` (`main`) · **Date:** 2026-10-15 · **Toolchain:** GAMS 54.2.1. The egypt/shale re-solves were all classified **`licensed`** from their own retained listings (retention patch, throwaway worktree, `EXIT`-trap cleanup).

**Scope:** traces and probes only. Every probe used scratch harnesses **outside the repo** that patch functions in-process; `src/` and `tests/` are untouched. The one new file outside this doc is the issue it files, **#1755**.

**Method rule, applied throughout:** a layer is named only after **instrumentation shows the first point where the output is wrong**, never from the name of the function where it becomes visible. Three of Sprint 38's four Phase-0 gates named the wrong layer. This task would have repeated that twice: turkpow's minted alias, and the diagonal defect's dropped constraint.

---

## Summary

| track | named surface (the hypothesis) | traced layer (the finding) | verdict |
|---|---|---|---|
| **P4 — turkpow Class A** (4.1) | `t__kkt1` minted into both coordinates of `vs(t,v)` | **KKT re-symbolisation:** `_replace_indices_in_expr`'s alias layer maps a stray **sum binder `v`** to `t`. The binder is left symbolic, **by design** (#720/#1085), in the AD's full-collapse condition. The mint is **downstream** and only renames an already-collapsed `vs(t,t)` | 🔶 layer right, site wrong |
| **P4 — egypt / shale** (4.2) | the Class-A reference dominates each mismatch | Both references are **live** collapses: restoring the hand-derived term **changes** PATH's path in each. But both stay **MS 5**, so another defect sits underneath. *(A first shale patch zeroed an already-zero coefficient, which tested nothing; corrected in review, see §2)* | ❌ |
| **P4 — Class B** (4.3) | the IR records whether a repeated-symbol domain is a declaration or an assignment context | **confirmed, it is in the IR**: `ParameterDef.domain` (declaration) vs `ParameterDef.expressions[k][0]` (assignment LHS). gussrisk's fix layer is **emit** (`emit_post_assignment_na_cleanup`) | ✅ |
| **P7 — diagonal defect** (7.1, 7.2) | "probably `_diff_sum`" | reproduces on `main`, **worse than reported**: the constraint and its multiplier are **dropped entirely**. Layer: **AD**, `derivative_rules._sum_should_collapse`, whose `len(sum_index_sets) != len(wrt_indices)` early return rejects a reference repeating one binder. **Filed: #1755** | ✅ / 🔶 |
| **P8 — structural sites** (8.1) | no discriminating input exists | **both guards are live:** a 3-D aliased input changes the **emit** with each consume-once guard disabled, so both can be promoted to **behavioural** pins | ✅ |
| **#1737** (8.2) | no planned change routes through the refusal | **P6 E1–E4: no.** **P7 (#1755) and P4: yes, indirectly.** The refusal scans equalities **and inequalities** whose multiplier is **referenced** (all inequalities when no referenced set exists), so a fix that newly references a multiplier exposes its equation's domain to the refusal | 🔶 |

---

## 1. turkpow — Class A (Unknown 4.1)

**Baseline:** `make check-index-repeats` → `P1 OK: 0 violation(s) in 3109 head(s)`, **`P2: 9 violation(s) across 6 model(s); baseline 9`**. turkpow contributes 3: `vs(v,v)`, `vs(t__kkt1,t__kkt1)`, `vs(t__kkt2,t__kkt2)`.

**The emitted reference** (`stat_zt(m,v,b,t)`, golden L208): `sum(t__kkt1, ((-1)*(opcostt(m,v,t__kkt1)*dur(b)*1$(vs(t__kkt1,t__kkt1))))*nu_ao(v))`.
- **The source:** `ao(t).. phio(t) =e= … + sum((mt,v)$vs(t,v), opcostt(mt,v,t)*sum(b, dur(b)*zt(mt,v,b,t)))`, with `Alias (t,v)`.
- **The correct term:** **`-opcostt(m,v,t)*dur(b)*nu_ao(t)$vs(t,v)`**. `zt` is on the **RHS** of `ao` (golden L246), so the LHS − RHS convention gives a **negative** coefficient, matching the captured AD derivative's `(-1)*(…)` below. `stat_phio` uses `+nu_ao(te)` for the LHS's `phio`, so the multiplier convention is not reversed. *(An earlier revision omitted the minus sign; PR #1756 review.)*
- **What is lost:** the multiplier's index (`nu_ao(v)` should be `nu_ao(t)`) and the guard's second coordinate.

**Traced backwards, with instrumentation at each step:**

1. **The minting spy.** `_get_or_create_fresh_alias` records **exactly two** mints in a turkpow translate (`t → t__kkt1`, `t → t__kkt2`), both from `_add_indexed_jacobian_terms:7624`, reached via `build_stationarity_equations:2548` → `_build_indexed_stationarity_expr`.
   - **Positive control:** the same spy fires on `sambal` (`i → i__kkt1`), whose emit is **correct** (`xb(i,i__kkt1)`, two distinct coordinates, equal to its golden) and which has **no** P2 violation. So minting itself is legitimate.
2. **Before vs after the mint's rename** (`_rewrite_subset_to_superset`, rename `{t: t__kkt1, bp: b}`): the input is **already** `… 1$(vs(t,t)) … nu_ao(v)`. **The coordinate is lost before the mint**, which then renames `t` uniformly and correctly for its input.
3. **The first wrong output** (`_replace_indices_in_expr`): input `vs("1983", v)`, output **`vs(t,t)`**, with the ChainMap `{'gas-t':'m', '1978':'v', 'high':'b', '1983':'t'}`, `{'bp':'b', 'v':'t'}`, …. The concrete label `"1983"` correctly becomes `t`. The **bare symbol `v`** is sent by the alias layer `{'v': 't'}` to `t`, although `v` is a distinct position of `zt(m,v,b,t)`.
4. **Why a bare `v` is there at all:** the AD derivative, captured inside the pipeline, is `(-1)*(opcostt("gas-t","1978","1983")*dur("high")*1$(vs("1983",v)))`. On a **full** sum collapse, `derivative_rules` deliberately keeps the condition symbolic (~L2925–2933, issues #720/#1085: "so that `_replace_indices_in_expr` can correctly map them to the stationarity domain"). **That contract breaks when the sum binder (`v`) is an alias of another variable-domain index (`t`)**: the alias layer resolves it to the wrong position.

**Layer: KKT / stationarity re-symbolisation** (`src/kkt/stationarity.py::_replace_indices_in_expr`, its alias ChainMap layer), consuming an AD output that is symbolic by design.
- **Justification:** the AD output is exactly what #1085 specifies, and the mint is downstream. The first wrong value is produced by `_replace_indices_in_expr`.
- **Fix direction:** a binder that appears in the variable's domain at its own position must map to **that** position, not to its alias root's first occurrence. Or the full-collapse path substitutes the matched concrete label for the binder, as the partial-collapse path already does (~L2921). That second option is wider, because it reverses #1085's choice.

**Phase-0 outline (P4, Class A):**
- **Layer:** KKT re-symbolisation (above).
- **Fail-before:** a synthetic `Alias (t,v)`, a variable `z(v,t)`, and an equation `e(t).. sum(v$s(t,v), c(v,t)*z(v,t)) =e= …`. Assert **P2 holds** on the emit: no `$(…)` guard repeats a coordinate, and the multiplier is `nu_e(t)`.
- **Positive control:** the same fixture **without** `Alias` (distinct sets) already passes, so the test can tell the two apart.
- **Ratchet:** **9 → ≤ 6** (turkpow's 3), with `--update-baseline` **in the same commit**.
  - ⚠ Two of the remaining 6 are **nonsharp**, a MINLP (binary `y`). The translator now **refuses** it at the discreteness gate, it is excluded and never relaxed, and its golden predates that gate. **No fix can lower those two by regeneration.** The ratchet's realistic floor for P4 is therefore lower bounded by them.

## 2. egypt and shale — does the Class-A reference explain the mismatch? (Unknown 4.2)

**Hand-patch experiment, licensed** (throwaway worktree with the retention patch; each solve's own listing classified; worktree removed by the `EXIT` trap). Every invocation: edition **licensed**, solver **PATH**, **0** compile errors, `head_sha` `b85afbc0`.

| run | invocation id | MS | objective | iterations | attribution |
|---|---|---|---|---|---|
| egypt, golden | `egypt_golden_mcp.1792102178098244000.44319` | 5 | 1,448,953.756 | 62,176 | `MCP-FAILED` / own |
| **egypt, patched** | `egypt_patched_mcp.1792102184393261000.44344` | **5** | 11,645,180.0 | 69,730 | `MCP-FAILED` / own |
| shale, golden | `shale_golden_mcp.1792102188641554000.44350` | 5 | 2.38635e-11 | 23,304 | `MCP-FAILED` / own |
| shale, first patch (**vacuous**, see below) | `shale_patched_mcp.1792102191845932000.44365` | 5 | 2.38635e-11 | 23,304 | `MCP-FAILED` / own |
| shale, golden (re-run) | `shale_golden_mcp.1792161350233229000.95548` | 5 | 2.38635e-11 | 23,304 | `MCP-FAILED` / own |
| **shale, `cpu` coupling restored** | `shale_cpufix_mcp.1792161357634590000.95572` | **5** | 1.816195e-07 | **33,238** | `MCP-FAILED` / own |

NLP references: egypt **4,134,175.7019**, shale **9,354.8644**.

- **The egypt patch** (`stat_trans(c,r,rp)`): the golden's single term `-(1$(tranc(rp,rp)))*nu_fodb(r,c)` is replaced by the hand-derived pair.
  - **The source:** `fodb(r,cf).. fodder(r,cf) =e= … + sum(rp$tranc(r,rp), trans(cf,rp,r) - trans(cf,r,rp))$ct(cf)`.
  - **Sign convention**, checked on `stat_xcrop`: coefficient = d(LHS − RHS)/dx.
  - **The derivative w.r.t. `trans(c,r,rp)`:** **`+ nu_fodb(r,c)$tranc(r,rp) − nu_fodb(rp,c)$tranc(rp,r)`**, under `$ct(c)$cf(c)`.
  - **What went wrong:** the golden's collapsed term fits a **diagonal representative instance** (`r = rp`), where the two terms cancel.
  - **The result:** PATH's path changes (iterations and terminal objective both move), so the reference is **live**. But the model stays **locally infeasible**, so the Class-A reference is **not the dominant cause**.
  - **Consistent with Task 7:** egypt's `--nlp-presolve` emit fails to compile (`$140`, R-PRE-140), which is a second defect.
  - MS-5 objectives are terminal values at an infeasible point, so neither run "moves toward" the NLP objective in any meaningful sense.
- **shale. The flagged reference is a live collapse, and the first patch was vacuous** (PR #1756 review).
  - **The source:** `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1`, strictly lower-triangular, and `t(tf)`. `ts(tf,tf)` appears twice in `stat_h(m,tf)`:
    - **In the `acap` offset-0 term:** legitimately zero, since the diagonal of `ts` is 0.
    - **In the `cpu` term:** `((-1) * 1$(ts(tf,tf))) * lam_cpu(m,tf)`, the **diagonal only**, which is always 0. The source is `cpu(m,t).. sum(p, b(m,p)*z(p,t)) =l= sum(tf$ts(t,tf), h(m,tf))` (`comp_cpu`, golden L363), so the correct contribution is **`-sum(t$ts(t,tf), lam_cpu(m,t))`**: every row `t` the cell feeds. **The whole `cpu` coupling into `stat_h` is lost.** That is the Class-A coordinate collapse, not an inert reference.
  - ⚠ **The first patch (`1$(ts(tf,tf))` → `0`) tested nothing.** It replaced an already-zero coefficient with zero, so the "identical solve" compared the defective row with itself.
  - **Corrected experiment:** the `cpu` term is replaced by `((-1) * sum(t$(ts(t,tf)), lam_cpu(m,t)))` and re-solved licensed. PATH's path **changes** (23,304 → **33,238** iterations; terminal objective 2.39e-11 → 1.82e-07), so the reference is **live**. But the model stays **MS 5**, so **the restored coupling is necessary but not sufficient**: another defect sits underneath, as with egypt. Task 7's shale presolve `$148` is the named candidate.

**Phase-0 consequence:** P4 must not claim egypt or shale as Class-A recoveries. **Both references are live collapses, and fixing each is necessary, but neither fix is sufficient.** The defect underneath must be diagnosed first (egypt: R-PRE-140 and its cold MS 5; shale: its cold MS 5, with the presolve `$148` as the candidate). The hand-derived terms above are each one's correctness reference.

## 3. Class B — is the context in the IR? (Unknown 4.3)

**gussrisk, traced source → IR → emit:**
- **Source:** `covar(stocks,stocks)` declared under `Parameter`; assigned `covar(s,sp) = sum(e, …)/card(e)` with `Alias (stocks,s,sp)`.
- **IR:** `ParameterDef(name='covar', domain=('stocks','stocks'), values=None, expressions=[(('s','sp'), <expr>)])`. **The declaration domain and the assignment's LHS index tuple are both recorded.**
- **Emit:** the flagged line is the **NA-cleanup**: `covar(stocks,stocks)$(NOT (covar(stocks,stocks) > -inf and covar(stocks,stocks) < inf)) = 0;` (golden L52). It is built from the **declaration** domain, so in GAMS it touches only the **diagonal**, while the assignment filled the full matrix.
  - **Layer: emit**, `src/emit/original_symbols.py::emit_post_assignment_na_cleanup`.

**Rule sketch:** index the cleanup by **distinct per-position symbols**: the assignment's LHS tuple, or fresh aliases of the declared set where the declaration repeats a symbol. Never by the raw declared domain. Against the three Class-B fingerprints:

| fingerprint | rule applies? | note |
|---|---|---|
| gussrisk `covar(stocks,stocks)` | **yes**: this is the NA-cleanup case | |
| shale `ts(tf,tf)` | no | a stationarity guard, not NA-cleanup. Its `cpu` occurrence is a live Class-A collapse (§2); its `acap` offset-0 occurrence is legitimately zero |
| nonsharp `inter(col,col,stm)` | no | ⚠ **nonsharp is discrete (MINLP), out of scope and refused by the translator.** Its stationarity reference also reads as the Class-A row/variable alias collapse, not a context problem, but that reading is from the golden only and cannot be exercised |

## 4. The diagonal-reference defect (Unknowns 7.1, 7.2) — filed as #1755

**The reproducer, on `main`:** `diagsum(j).. sum(i, tsam(i,i)) =e= 1;` with `Alias (i,j)`.
- **Linear objective:** emits exactly **`stat_tsam(i,j).. 1 =E= 0;`**.
- **Quadratic objective:** emits `2 * tsam(i,j) =E= 0`.
- **In both, `diagsum` and `nu_diagsum` are absent from the MCP**, so the defect drops the **constraint**, not only a term.

**Is the term really dropped, or is the row legitimately trivial?** Dropped. The scalar variant `diag.. sum(i, tsam(i,i)) =e= 1` with objective `sum((i,j), sqr(tsam(i,j)))` has the NLP optimum MS 2 at **0.3333**.
- **Hand-derived row:** `stat_tsam(i,j).. 2*tsam(i,j) + nu_diag$(sameas(i,j)) =E= 0`, with `diag` restored and paired with `nu_diag`.
- **The patched MCP solves MS 1 at 0.333**, with `tsam = 0.333` on the diagonal.

**Layer, by instrumentation:**
- `differentiate_expr` inside the pipeline returns **0 for all nine instances**, including the diagonal `('i1','i1')`.
- A `sys.settrace` of one diagonal call gives `_diff_sum` → **`_sum_should_collapse` → `False`** → `_diff_varref(tsam(i,i))` vs `('i1','i1')` → `_alias_match` → `None` → `Const(0)`.
- **The cause:** `_sum_should_collapse` (`src/ad/derivative_rules.py`, ~L2974) begins with **`if len(sum_index_sets) != len(wrt_indices): return False`**. It pairs binders with positions positionally, so one binder used in two positions (1 ≠ 2) can never collapse, even when both positions carry the same value.
- **Downstream:** with an all-zero row, `nu_diagsum` is never referenced, and the equation is pruned with it. That pruning is **not** the empty-equation detector (§6).

**Corpus scope:** `grep -E '^stat_\w+(\([^)]*\))?\.\.\s*-?\(?\s*-?[0-9.]+\s*\)?\s*=E=\s*0;'` over the goldens finds only `saras` (`0 =E= 0`, five rows: a different, zero-valued shape, and saras is on the staleness allowlist). The positive control holds: the same pattern **matches** the reproducer's row. So no golden carries the **constant-only** form. A dropped term in a row that keeps other terms is **not** detectable by this grep.

**Issue:** `docs/issues/ISSUE_1755_sum-repeated-binder-never-collapses.md` · [#1755](https://github.com/jeffreyhorn/nlp2mcp/issues/1755).

**Phase-0 outline (P7):**
- **Layer:** AD (above).
- **Fail-before:** the reproducer emits `1 =E= 0` and no `nu_diagsum`.
- **Pass-after:** `diagsum` and `nu_diagsum` are present, `stat_tsam` carries `nu_diagsum` on the diagonal, and the scalar variant solves to 0.3333.
- **Positive control:** the off-diagonal instance `tsam('i1','i2')` still differentiates to **0**.
- **Corpus:** the full leak gate, **complete**. Any golden that changes is a candidate corpus instance, to be examined, not blindly refreshed.
- ⚠ **And see §6:** fixing this newly references multipliers, which can expose a repeated equation domain to #1737's refusal.

## 5. The two structural-only sites (Unknown 8.1)

Sprint 39's nine 2-D shapes left both guards byte-identical. Extended to **≥ 3-D, subset-of-subset, alias and offset-shaped** inputs, with each consume-once guard disabled by rebuilding the function from its own source with the one condition neutralised (`_match_subset_domain`: `if k in used_var_positions:`; `_compute_index_offset_key`: `vi not in used_var and`).

**Function level:**

| function | shape | guard on | guard off |
|---|---|---|---|
| `_match_subset_domain` | 2-D subsets, equal length | `{ii: i, jj: ip}` | same |
| | **3-D, own position fails → scan** (`(ii,jj)` vs `(i,k,ip)`) | `{ii: i, jj: ip}` | **`{ii: i, jj: i}`** |
| | 3-D, three subsets onto `(i,ip,ipp)` | `{ii: ipp, jj: ip}` | same |
| | subset-of-subset (`iii ⊂ ii ⊂ i`) | `None` | same |
| | **alias-only, 3-D** (`(ip,ipp)` vs `(i,k,ipp)`) | `{ip: i}` | **`{ip: i, ipp: i}`** |
| `_compute_index_offset_key` | **2-D eq `(i,ip)` vs 3-D var `(i,k,ip)`** | `(1, 999, 1)` | **`(3, 999, 999)`** |
| | **2-D eq `(i,tp)` vs var `(i,k,i)`** | `(1, 999, 1)` | **`(3, 999, 999)`** |
| | **subset eq `(ii,jj)` vs var `(i,k,ip)`** | `(1, 999, -1)` | **`(2, 999, 999)`** |
| | subset-of-subset eq `(iii,jj)` | `(1, 999, 999)` | same |
| | **offset-shaped eq `(i,ip)` vs var `(ip,k,i)`** | `(2, 999, -1)` | **`(0, 999, 999)`** |

**Emit level** (the task's positive control: a broken guard must change the **emit**). The guard-on emits are deterministic (identical hashes across two runs).

- **`msd3`:** `c(ii,jj).. sum(k, x(ii,k,jj)) =l= 1`, `x(i,k,ip)`, `Alias (i,ip)`.
  - **guard off:** `lam_c(i,ip)` → **`lam_c(i,i)`** in both the declaration and `stat_x`. That is the Class-A coordinate collapse.
- **`oik3`:** `e(i,ip)$(…).. sum(k, x(i+1,k,ip-1)) =l= 1`.
  - **guard off:** `lam_e(i-1,ip+1)` → `lam_e(i,ip)`. The lead/lag offsets are lost.

**Verdict:** **both guards are live, and each has a discriminating input that reaches the emit.** Both structural-only pins can be **promoted to behavioural pins**, asserting these emits, or the function outputs above.

**Phase-0 outline (P8):**
- **Layer:** KKT (`stationarity.py`).
- **The pin:** the two 3-D fixtures' emits (or the function-level tables) asserted with the guards in place.
- **Positive control:** the same assertion **fails** with the guard neutralised, as above. This becomes the mutation test that `test_positional_domain_sites.py`'s structural rows lack.

## 6. #1737 — does a planned change route through the refusal? (Unknown 8.2)

`src/kkt/empty_equation_detector.py` has **one caller**: `src/emit/emit_gams.py:3631` (`detect_empty_equation_instances`). Its #1737 guard is `assert_no_repeated_symbol(eq_def.domain, …)` (L130). **It is called twice:**
- **for equalities** (`relevant_eqs`: equalities whose multiplier is in `kkt.referenced_multipliers`);
- **for inequalities** (`emit_gams.py` ~L3662–3675: `relevant_ineqs`, `include_inequalities=True`; **every** inequality when no referenced set exists).

**Both scans reach the repeated-domain assertion** (PR #1756 review: an earlier revision described the equality scan only).

| planned change | changes equation domains? | changes `referenced_multipliers`? | routes through the refusal? |
|---|---|---|---|
| P6, Task 9's E1–E4 (filters, sparse validation) | no | **no**: byte-identical by construction | **no** |
| P6, E5/E6 (`simplify` recursion) | no | only if simplification changes which terms survive | conditional: needs its own check |
| **P7, #1755** (`_sum_should_collapse`) | no | **yes**: it restores multipliers like `nu_diagsum` | **yes, indirectly** |
| **P4, Class A** (re-symbolisation) | no | possibly: it restores dropped terms (egypt's `nu_fodb(rp,c)`; **shale's inequality multiplier `lam_cpu(m,t)`** via the inequality scan) | **possibly**, through either scan |

**Demonstrated, not inferred:** two tiny models with a **repeated equation domain** `dd(i,i)`.
- **(a)** `dd(i,i).. sum(j, tsam(j,j)) =e= 1`: the multiplier is **unreferenced** (#1755). Exit 0: **`dd` is silently dropped, and no refusal fires.**
- **(b)** `dd(i,i).. x(i) =e= 1`: referenced. Exit 1: **`Error: Invalid model - empty-equation scan of 'dd': domain ('i', 'i') repeats ['i'] …`.**
- **The same holds for an inequality** whose multiplier becomes referenced: the inequality scan reaches the same assertion. *(By code reading: the same function, `include_inequalities=True`. Only the equality case above was executed.)*
- **So the P7 fix turns models of shape (a) from silently wrong into refused.** That is the correct direction, but it is a **visible behaviour change** P7's gate must expect, and #1737 must remain untouched.
- `test_the_AD_collapse_is_reachable_but_EMIT_refuses_it` **passes** (1 passed).

## 7. Phase-0 outlines — the P10b field (layer + positive control)

| track | layer | fail-before | positive control | ratchet / gate |
|---|---|---|---|---|
| P4 Class A (turkpow) | KKT re-symbolisation (`_replace_indices_in_expr`, alias layer) | synthetic `Alias (t,v)` fixture: P2 holds on the emit; the multiplier is indexed by the equation index | the same fixture with distinct sets passes before and after | P2 **9 → ≤ 6**, `--update-baseline` in the same commit (nonsharp's 2 cannot move: out of scope) |
| P4 egypt/shale | **live Class-A collapses, each necessary but not sufficient**, plus an undiagnosed second defect (egypt: R-PRE-140; shale: cold MS 5, presolve `$148`) | each golden's flagged term (above) | restoring the hand-derived term changes PATH's path (both models) | **do not book as Class-A recoveries** until the defect underneath is fixed |
| P4 Class B (gussrisk) | emit (`emit_post_assignment_na_cleanup`) | the cleanup touches only the diagonal | a non-repeated parameter's cleanup is unchanged | P2 −1 |
| P7 diagonal (#1755) | AD (`_sum_should_collapse`) | the reproducer emits `1 =E= 0` and drops `diagsum` | the off-diagonal derivative stays 0; the scalar variant solves to 0.3333 | leak gate complete; expect #1737 refusals for shape-(a) models |
| P8 structural sites | KKT (`_match_subset_domain`, `_compute_index_offset_key`) | — (a promotion, not a fix) | the guard neutralised → the emit changes (§5) | 2 structural pins → behavioural |
