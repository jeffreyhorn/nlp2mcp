# Sprint 41 — Carryforwards from Sprint 40

**From:** Sprint 40 close, `ca83e884`, 2026-11-07 · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01** / schema **3.1.0**
**Baseline for Sprint 41 (continuity, 140):** Solve **114** · Match **96** (65 cold + 31 presolve) · Translate **135** · mi **13** · pse **6** · `path_solve_terminated` **2** (ferts, tabora — C1 influx, in cohort) · `path_solve_license` **0** · all-219 Match **101** · genuine floor **76** (+0 license-unlocked, not counted)
**Current (149 = 140 + 9 admitted):** Solve **116/139** · Match **98/149** (65 cold + 33 presolve) · Translate **139/146** · mi **13** · pse **7** · pst **3** (+minsurf, NLP-gated admitted)

> Every figure here is derived at `ca83e884`. **Anything quoted in a Sprint-41 doc must carry its commit** — Sprint 39 shipped a floor figure that the provenance file disagreed with, and Sprint 40 had a Day-10 Match correction that Day 8's #1787 forecast; a line that does not carry its commit cannot be audited across the twelve-day arc.

**This file is a convention, not a prompt item.** The Day-13 prompt lists SPRINT_LOG, SPRINT_RETROSPECTIVE and the SUMMARY row; the next sprint's prep looks for `SPRINT_41_CARRYFORWARDS.md` by name (S33 → S40 unbroken, S39 → S40 included the Day-0 Floor-decision brief as the top item).

---

## 1. sroute's DB row is deliberately stale — Sprint 41 Day 0 should run the attribution check

**The situation.** Day 8 #1787 landed a multi-reference Jacobian fix that made sroute's cold emit solve. Day 10 CK2 confirmed the re-solve produces a presolve match. Day 11 P9a deliberately did **not** persist sroute, because the licensed cohort CI run (42399418829) at close shows sroute produces its own `MODEL STATUS 1 Optimal` that matches the embedded NLP's answer — the S38 D9 `weapons` spurious-match shape. The current DB row is `model_infeasible + not_tested`; the live run is a match.

**Why this is not just a persist.** If the MCP's own solve produced an own answer, sroute is a real match (Match +1, counted). If it produced an aborted solve and `nlp2mcp_obj_val` carried the embedded NLP's answer as `tetd.l`, the match is spurious (same shape S39 corrected weapons for) and the row should be `path_solve_terminated` — the outcome `scripts/gamslib/test_solve.py:1426–1461` maps an attribution-rejected apparent success to, not a manufactured `model_infeasible` (an aborted or embedded-only solve does not establish MCP infeasibility).

**Bounded next step:** **Sprint 41 Day 0 runs the attribution-aware pipeline on sroute** (and on any cohort row whose MCP produces `MODEL STATUS 1 Optimal` that matches the embedded NLP) and persists whatever `scripts/gamslib/test_solve.py` returns — a real match if `Attribution.mcp_succeeded` holds (ownership of the *last* summary from our emitted MCP + solver completion + model status in {1, 2}, with abort-safety predicates; see `scripts/sprint_audit/check_mcp_solve_attribution.py:352–384`), `path_solve_terminated` if the attribution is rejected. **Decide the shape of the general rule at the same time** — the fingerprint is "own-optimal + match" in a row whose warm-started MCP never took ownership of the final `MODEL STATUS`. S38 D9 saw it, S39 D10 corrected it, S40 D11 decided not to reach it. Three sprints is enough.

**⚠ Record the decision as a rule, not a checklist item.** The `weapons` → `sroute` pattern says *every* own-optimal match in a license-unlocked row needs an attribution verdict before persistence; adding sroute to a Day-0 one-off is treating a class as a case.

## 2. abel's DB row is stale — Day 10 CK2 noted; carried as a stale-row correction

Day 10 CK2 noted `abel` moved `mismatch → match` on re-solve. It is not in the cohort (not license-gated), so its stale row is a plain refresh, not a license-neutrality call. **Bounded next step:** on the Sprint 41 Day-0 cohort re-run (above), include abel; a successful match persists `model_optimal + match` with `edition=None` or whatever the first-licensed run attaches.

## 3. P5 #1789 stat_step / scalar-offset — BANKED, mechanism confirmed, three defects named

**Day-9 prototype** reached the **lead/lag fixtures at 68.546 = NLP** on the `_add_jacobian_transpose_terms_scalar` offset handler + `_apply_offset_substitution(deriv, eq_idx, eq_idx, mult_domain, …)` — fixture success on a controlled input, not a corpus match. A **separate, pre-existing unresolved defect** was observed **in the same function** (SPRINT_LOG line 1284, "a second mechanism in the same function"): `_replace_indices_in_expr` **lifts** a quoted literal `u('h3')` to the bare symbol `u(h)`, giving `2*u(h)` — the lift itself is the bug. **The prototype neither causes nor fixes this;** it was recorded on #1789 as a third gate form, as a Sprint-41 item independent of the +1 target (named below). The **full REPLAN gate fired on Day 10:**

| control | result |
|---|---|
| robot, rocket | **⛔ BACKWARD** — `path_solve_terminated` (division by an out-of-range `i_the(h0)` = UNDF; needs a **boundary guard**, not a reindexing) |
| lnts | residual **got worse**, 9.66 → **13.26** — a second, unattributed defect that the +1 revealed rather than fixed |
| glider | row came out **wrong** — `sum(h, … vel(c,h) …)` on a subset domain (the subset domain resolves through the parent set) |

**Durable commit:** [`f57bc1d7`](https://github.com/jeffreyhorn/nlp2mcp/commit/f57bc1d7eee0ba0af7aee42e8ac9271e4c103e91) on branch `banked/1789-scalar-offset` (fix + 4 unit tests, against `1abcd687`; **not for merge**). The diff + three mechanisms are also on #1789.

**Bounded next step:** **the defects are independent and should be fixed separately,** with a Phase-0 doc each:
1. the **boundary guard** on the scalar-offset substitution (robot/rocket's UNDF root);
2. the **subset-domain resolution** for `sum(h, …)` where `h` is a subset coord (glider's wrong row);
3. lnts's **second defect** — unattributed; if the Day-9 prototype made lnts worse, something in the handler is wrong independently of the +1. Trace from the stationarity entry, not the emitter;
4. the **quoted-literal lift** — `_replace_indices_in_expr` incorrectly lifts `u('h3')` to `u(h)`; the prototype neither causes nor fixes this (SPRINT_LOG line 1284). It is a pre-existing, independent defect on the same function, with its own Phase-0 doc.

Do **not** re-apply the banked diff verbatim; it moved two models BACKWARD and one wrong. The +1 target (the lead/lag fixtures' 68.546) is real as a **fixture result**; the delivery mechanism to a corpus match is not.

## 4. P6 E5/E6 sarf recursion — THREE filed issues, recursion diagnosed as a SHAPE defect

**#1795 (Primary):** the `lam_labor` `$`-guard in sarf's `stat_task` is a **51,792-tuple left-deep OR** built by `_build_tuple_or_guard`. The semantics are right (the `labor` rows reference a non-Cartesian subset of task instances, so the #1381 follow-up correctly refuses a per-dimension AND); the shape is not. **Fix surface:** emit the guard as a **declared set** with a membership test, instead of inlining every tuple as an OR of 4-`sameas` conjunctions. ⚠ Needs a guard-impact review, because `stationarity.py` holds #1741's guard.

**#1796:** `t++(expr)` with an expression amount renders as a circular lead/lag; sarf writes `luse(c,t++(cs(c,"start",s)-1),s)` for `MCP compile line 365`. Scratch fix verified.

**#1797:** zero-padded numeric ranges (`t / 01*24 /`) lose the padding and render as `1..24`. A grep finds sarf the only corpus user; scratch fix verified.

**Day-10 measurement, for Sprint 41 planning:** with the balanced-OR-tree scratch patch, sarf **translates in 338.2 s** (load 10–16) and **MCP compiles with 0 errors** — but GAMS generation does not finish in 37 min. `gamscmex.out` runs at 100 % CPU; no solver starts. The file carries **207,218 `sameas` calls**, and the guard is evaluated for each of `stat_task`'s 369,024 instances. **The shape-not-algorithm fix (#1795) is the right one; tree-balance + render-fix are not enough on their own.**

**Bounded next step:** **#1795 first** (the shape), then #1796 and #1797 together (both one-off render fixes). Expect translation to drop well below 300 s once the guard stops being 51,792 OR terms.

**C7 re-registration for Sprint 41:** the +1 Translate target stands, but the precondition should now be *P6 #1795 implementation started* (a start-state fact, per CONTRIBUTING.md §8c and SPRINT_40/PLAN.md §5) — not "landed", which is an outcome. **Success criteria** (not preconditions): #1795 lands, and sarf produces a byte-stable golden at ≤ 300 s. The distinction matters: a sprint that attempts #1795 and fails to land it should close C7 **UNMET**, not VOID; VOID is reserved for the case where the precondition itself does not hold (implementation never started). Sprint 40's precondition — *P6's E5/E6 item started* — was correct for Sprint 40 because E5/E6 was unscoped then. The three filed issues are the scope now.

## 5. The license-unlocked COLD-match ledger has zero production entries — the contract and implementation are complete

**C5 says a license-unlocked cold match goes in the non-counting `license_unlocked` ledger.** This sprint's dry run predicted zero entries; the sprint delivered zero entries. **Zero production entries is not the same as missing implementation:** the ledger's contract was decided by owner Decision 1 (answered 2026-10-14 at `b44344a2`, amended into `data/floor_provenance.json`'s README at lines 20–35); the writer-side schema is committed as `_license_unlocked_schema` in `data/floor_provenance.json` (fields: `model_id`, `limb` — must be `"license-unlocked-cold-match"` — `since_sprint`, `evidence`, `pr`); the reader (`floor_tracker.license_unlocked`), validator (`floor_tracker.validate_entries` — required-field check, limb equality to `LEDGER_LIMB`, "model may not appear in both `entries` and `license_unlocked`", duplicate detection), and side-by-side reporter (`floor_tracker.py` main path: `"Genuine floor: {floor} (+{len(ledger)} license-unlocked, not counted)"`) are all implemented and exercised on every `floor_tracker.py` invocation this sprint (output: `+0 license-unlocked, not counted`).

**Bounded next step:** when a license-unlocked **cold** match first appears (sroute would be a presolve match, not cold — presolve-only matches never enter the ledger, per the README), append one entry under the committed schema (`model_id`, `limb: "license-unlocked-cold-match"`, `since_sprint`, `evidence`, `pr`). There is no format decision to take with the owner: the format is decided and committed, and `floor_tracker.py`'s validator will refuse any entry that deviates from it.

## 6. `path_solve_terminated` is populated, by design — C1's population list is now a living set

Three models sit at `path_solve_terminated` at close, all with **MCP-generation errors** diagnosed on #1767 (not NLP infeasibility): **ferts** (cohort, EXECERROR 36 — 36× empty-equation `comp_mb.lam_mb` pairs whose multiplier is left free), **tabora** (cohort, EXECERROR 36 — 36× empty-equation `comp_lb.lam_lb` pairs whose multiplier is left free), **minsurf** (NLP-gated admitted, EXECERROR 4 — four unmatched corner-fix equations `v_fx_<corner>.nu_v_fx_<corner>` at the boundary corners `x0_y0`, `x0_y26`, `x51_y0`, `x51_y26`). All three are in the **two populations** C1 names; the "0 outside" measurement holds.

**Bounded next step:** **Sprint 41 should fix the emitter's empty-instance handling for inequality multipliers** (ferts/tabora: for instances whose body is data-conditioned away, fix the multiplier via `lam.fx(...)$(row empty) = 0`; same class as #1041 cesam2 and completed ISSUE_1021 spatequ) and the per-element `.fx` emission at doubly-fixed corner points (minsurf; plus the stationarity defect R-B-minsurf #1771 that affects it independently). Not an NLP-solver effect — these are MCP generation errors; a GAMS version bump will not move them.

## 7. The P2 index-repeat ratchet ratcheted 9 → 3 — carry the remaining three as an audit, not a defect

The P2 ratchet at close is **3**, and the remaining references are **not turkpow**. From `scripts/sprint_audit/index_repeat_p2_baseline.json` at close:

| model | reference | diagnosis |
|---|---|---|
| **dinam** | `ts2(te,te)` in `stat_ka` — a mixed direct + summed reference | **#1778's family**; see Day 8 log at line 1148 for the diagnosis and the Day-8 ratchet move that left this reference standing |
| **nonsharp** | `inter(col,col,stm)` | **refused MINLP** — regeneration cannot move its golden; a Phase-0 doc would need to attack the source declaration |
| **nonsharp** | `inter(col__kkt1,col__kkt1,stm)` | the same reference after KKT alias minting; same disposition as above |

**Bounded next step:** **the 3 are correctness-neutral as long as the guards fire 0 times in production**, and their verification routes differ by model. For **dinam**, Sprint 41 should re-trace `stat_ka` from the AD entry outward — the Day-8 log flags it as #1778's family, so start there. For **nonsharp**'s two references, the baseline cannot be moved by regeneration (MINLP out of scope); the right move is a reach probe on those two guards to confirm they never fire in the corpus (S39 D11 pattern — reach count on every leak-gate subprocess). If a reach is measured, re-open the item against the source declaration.

## 8. The licensed CI's isolation claim held — keep it in `main`-only and re-verify per release

**Every Sprint 40 PR workflow ran `edition=demo`, 10 of them.** Across the sprint window (2026-10-18 → 2026-11-07) the `gams-licensed` environment saw **13 `push` runs to `main` and 19 nightly `schedule` runs on `main`** (`gh run list --workflow=licensed-solve.yml`): every one that ran reported `edition=licensed` with the scan positive control hit and no `USER:` line. **The design works as designed.**

**Bounded next step:** **do not assume this across GAMS installer rotations.** The pinned SHA-256 in `licensed-solve.yml` is the only mechanism preventing a silent installer swap. Review the SHA at every GAMS version bump; if GAMS 55 ships, re-measure the discriminator (the `edition=licensed/demo` classification is based on a two-run probe against synthetic models; re-run them before changing the pinned version).

## 9. The attribution surface for own-optimal matches is the broader shape of item 1

**S38 D9 (weapons):** booked as match; the MCP produced no own `MODEL STATUS`; corrected in S39 D10 to mismatch.
**S40 D11 (sroute):** deliberately not booked; the MCP produces own MS 1 Optimal that matches the embedded NLP; attribution not yet run.

**The fingerprint:** a license-unlocked row whose MCP writes a `MODEL STATUS 1 Optimal` that matches `tetd.l` (or the equivalent warm-start variable) exactly, after a presolve retry. The *right* match discriminator is **`Attribution.mcp_succeeded`** — ownership (the *last* summary from `self.mcp_summaries`, our emitted MCP), solver completion (`solver_status == _NORMAL_COMPLETION`, with `not aborted` / `not abort_ambiguous` safety predicates), and model status (`model_status in _SUCCESS_MODEL_STATUS`); see `scripts/sprint_audit/check_mcp_solve_attribution.py:352–384` — **not** a per-step count. **Taking a solver step is not an attribution discriminator by itself:** a valid warm start can finish with zero iterations and still own its final `MODEL STATUS` (real match), while a solver can take many steps and abort before claiming ownership (attribution rejects it). Reading `tetd.l` alone proves neither ownership nor failure.

**Bounded next step:** **Sprint 41 item 1 runs `check_mcp_solve_attribution` once on sroute** (the immediate carry) and **decides whether that check becomes a persistence precondition for any license-unlocked own-optimal row** (the general rule). The rule shape beats the per-row shape.

## 10. The Day-13 close process held; record what moves to a prompt template

**Eight of nine close rules MET, one UNMET-not-VOID (C7), five take no precondition and all five are MET.** Three mechanisms that earned carry into the next sprint's prompt template:

1. **Pre-registering a rule whose precondition is "always", move it to the always-on list.** C1, C2, C5, C6, C8 have no precondition; they are rules, not bets. The rule-vs-bet distinction is where the pre-registration discipline earns its keep.
2. **Derive the affected set when the rule starts, not when it was planned.** C9's set was "prep's 7", amended at plan-write time to "derived at Day 11's start". Measured k = 12 ≠ 7; prep's list is the floor, not the ceiling. The same shape applies to any P-item that depends on a measurement taken after the P-item's planning.
3. **A rule that names a precondition it does not expect to hold is a bet on the plan, not on the work.** C7 was a bet on P6 reaching a Translate golden at ≤ 300 s. The precondition held (E5/E6 started), the goal missed. Neither voided nor met-weak; **UNMET** is the honest shape, and it is a different thing from "we did not try". Record UNMET-not-VOID in the close vocabulary; Sprint 41 may want it at the outset.
