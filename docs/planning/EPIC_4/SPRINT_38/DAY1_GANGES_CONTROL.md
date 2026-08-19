# Sprint 38 Day 1 — P1 ganges: direction-C control → **REPLAN**

**Date:** 2026-08-19 · **Branch:** `planning/sprint38-day1-ganges-control` · **Measured at:** `1e7b5023` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01** · **Scope:** `/tmp` control only. **`src/` was patched in the working tree and reverted; no `src/` change is committed.**

**Verdict: 🔶 REPLAN — and for a stronger reason than "it didn't work". #1668 direction 1 is a NO-OP: its stated premise is false.** The issue says the rebind *"rewrites the variable reference while leaving the parameter index untouched."* **It does not.** Measured over **265 rebind fires across three models: zero residual** — every `ParamRef` *and* every `VarRef` is rewritten. There is nothing for direction 1 to fix at the site it names.

**The asymmetry is real, but it is manufactured DOWNSTREAM** — by domain-position-driven re-symbolization in `stationarity.py`, not by `_diff_prod`. **So both #1668 directions are unimplementable at the rebind site**: direction 2 because the information isn't there (Task 4), direction 1 because there is nothing there to change.

**But the day also produced the most concrete P1 lead yet.** `bound_indices` is empty at the rebind site for a mundane reason: **stationarity peels the enclosing `Sum` and differentiates `sum_node.body`, never passing the binder down** — `bound_indices=` appears **zero times** in `stationarity.py`. **Direction A is a three-call-site change, not the deep refactor Task 4 priced.** It is banked untested; whether Day 2 pursues it is an owner call (§6).

---

## 1. What was tested

**#1668 direction 1 — "Rebind consistently: apply the same index substitution to parameter indices inside the collapsed factor, not only to variable references."**

Applied the banked `$149` rebind (`SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5) as a scratch patch at the `symbolic_name_match` branch of `_diff_prod`, with a read-only probe printing the expression **before and after** substitution, plus a **residual assertion**: after the rebind, does any `ParamRef` or `VarRef` in `log_term` still carry a rebind key as an index?

## 2. Direction 1 is a no-op — measured, not argued

### 2.1 The substitution is already total

| model | rebind fires | fires with residual `ParamRef` | fires with residual `VarRef` |
|---|---|---|---|
| prolog | 8 | **0** | **0** |
| camcge | 253 | **0** | **0** |
| lmp2 | 4 | **0** | **0** |
| **total** | **265** | **0** | **0** |

**Zero residual in 265 fires.** The reason is structural, not incidental: `_apply_index_substitution` dispatches `VarRef` and `ParamRef` through the *same* `_substitute_index` helper, which treats plain-string indices identically. There is no branch in which a parameter is skipped.

### 2.2 The AD layer's output is consistent — here it is

Probe at the rebind site, prolog, first fire (`rebind={'gp': 'food'}`):

```
PRE  log_term = … VarRef(p(gp)) ** ParamRef(eta(food,gp,enterpr)) … / VarRef(p(gp)) …
POST log_term = … VarRef(p(food)) ** ParamRef(eta(food,food,enterpr)) … / VarRef(p(food)) …
                              ^^^^                        ^^^^ BOTH rewritten
```

**Both moved.** Direction 1 asks for exactly this, and it is already what happens.

## 3. Where the inconsistency actually comes from

The emitted GAMS tells the other half of the story. `prolog`'s `stat_p(i)`, baseline vs rebind (**the only diff in the file, −3 bytes**):

```gams
- … prod(gp__, p(gp__) ** eta(g,gp__,h)) * p(gp) ** eta(g,gp,h) * eta(g,gp,h) / p(gp) / p(gp) ** eta(g,gp,h) …
+ … prod(gp__, p(gp__) ** eta(g,gp__,h)) * p(g)  ** eta(g,gp,h) * eta(g,gp,h) / p(g)  / p(g)  ** eta(g,gp,h) …
                                             ^^^^ variable moved          ^^^^^^^^^^ exponent did NOT
```

**So #1668's description is right about the emitted result and wrong about the cause.** At the AD layer both moved (§2.2). Between there and the emitter, the parameter's index **moves back**.

**The mechanism.** `_replace_indices_in_expr` (via `_build_constraint_element_mapping`, `stationarity.py:7919–7930`) lifts concrete elements back to symbolic set names **positionally against the declared domain**. prolog declares:

```gams
Alias (i,j), (g,gp);
   eta(g,gp,h) 'price elasticities';
```

`eta`'s positions 0 and 1 are **the same set under an alias**. So the AD layer's `eta(food,food,enterpr)` re-symbolizes position-wise: position 0 → `g`, **position 1 → `gp`** — *undoing* the substitution. `p(food)` has a single index and re-symbolizes to `p(g)`, *keeping* it.

**The rebind is consistent when made and inconsistent when rendered.** That is why no predicate at the rebind site can fix it, and why "substitute the parameters too" is a no-op: they *are* substituted, and then un-substituted.

## 4. The `$149` component still works on current `main` (Unknown 1.1, partially)

Per model, never inferred across the pair. Presolve variant; **counts read from GAMS's own `**** N ERROR(S)` line**, with printed markers shown only for continuity with the banked figures.

| | ganges baseline | ganges + `$149` | gangesx baseline | gangesx + `$149` |
|---|---|---|---|---|
| **GAMS total errors** | **199** | **178** | **199** | **178** |
| `gams rc` | 2 | **2** | 2 | **2** |
| `$141` printed markers | 48 | 48 | 48 | 48 |
| `$145` printed markers | 1 | 1 | 1 | 1 |
| **`$149` printed markers** | 1 | **0** | 1 | **0** |
| emit bytes | 86,462 | 86,425 | 85,850 | 85,813 |
| truncation notices | **2** | — | **2** | — |

**The `$149` half reproduces: 21 errors cleared on each model, `$149` to zero.** `rc` stays 2 **only because `$141` and `$145` were not applied** — this control tested direction C, not the full cascade.

**Note the truncation, again.** The baseline shows **199 errors but ~50 printed markers**, with 2 `Remaining errors not printed` notices. The banked per-code figures (78/3/9) are printed-marker counts and are **undercounts**; GAMS's total is the only sound reading. §4's totals are read that way.

**⇒ Unknown 1.1 is answered for the `$149` component and NOT for the full four-fix `rc=0` claim.** Re-establishing that would mean re-applying `a8ff626c` — a patch S37 Day 4 had to **correct mid-flight** as known-defective — to confirm a number Day 4 already measured per-model. **That is the "nursing" the plan explicitly warns against, and the cascade is not P1's blocker.** Stated as a bounded gap rather than papered over.

## 4a. Full-corpus leak sweep — the leak is exactly one model

Report-only (`check_golden_staleness.py --json`, **never `--fix`**), run against the patched tree over the full corpus:

```
Golden staleness: checked 163 in-scope golden(s) (7 allowlisted, 3 workers).
  3 golden(s) drifted from the current emit:
    DRIFTED: ganges_mcp.gms   (-37 bytes)
    DRIFTED: gangesx_mcp.gms  (-37 bytes)
    DRIFTED: prolog_mcp.gms    (-3 bytes)
```

| model | in `--expect-drift {ganges, gangesx, korcge}`? | verdict |
|---|---|---|
| ganges | ✅ | intended |
| gangesx | ✅ | intended |
| **prolog** | ❌ | **LEAK** — a live `model_optimal` + **match** model |
| korcge | ✅ allowed | **did not drift** — the `rPower` gate is not in this patch, so it was never going to |

**The leak is exactly one model, and it is the one S37 Day 4 found.** Scope asserted on **discovery** (163 in-scope of 170, 7 allowlisted), so this is a full sweep and not a silently narrowed one.

**A measurement-integrity note, since this sprint is about that.** The sweep completed in roughly its expected ~26 min, but appeared to run for **1 h 31 m** because the shell loop written to wait for it — `until ! pgrep -f check_golden_staleness` — **matched its own command line**, which contains the process name. A self-matching monitor never terminates. **It cost wall-clock only; no measurement was affected**, since the sweep's output was already complete and correct on disk. Recorded because "the watcher counts itself" is the same class as the gate-scope defects P6b exists to catch.

## 5. REPLAN — the pre-registered exit, taken the same day

The Day-1 exit fires on **either** clause, and **both** fire:

| clause | status |
|---|---|
| direction C misses `rc=0` on either model | **fires** — and it cannot do otherwise: direction C is a no-op, so its emit is byte-identical to the banked rebind's |
| perturbs anything outside `{ganges, gangesx, korcge}` | **fires** — the full-corpus sweep (§4a) drifts **exactly one** model outside the set: `prolog`, **−3 bytes**, a live `model_optimal` + match model. Direction C cannot change that. |

**Exit taken. `src/` reverted; the working tree is byte-identical to `main`** (verified by checksum, §7).

**Budget:** P1's remaining **~14 h moves to P8**, whose catalog was built in prep for exactly this (`BACKLOG_CANDIDATE_CATALOG.md`, 5 eligible candidates). **P8 is gated by P7**, so the reallocation lands on Days 11–12 as scheduled, not earlier.

## 6. Directions A and B — evaluated on paper, and A is much cheaper than priced

### 6.1 Direction A is a three-call-site change, and it is located

Task 4 priced direction A as *"find where the enclosing `Sum` is stripped … touches the shared differentiation entry path — full-corpus leak exposure."* **The stripping site is now identified, and it is not deep.**

**`stationarity.py` peels the `Sum` itself and differentiates the body:**

| site | call |
|---|---|
| `stationarity.py:659` | `differentiate_expr(sum_node.body, var_name, (sum_idx,), Config(...))` |
| `stationarity.py:877` | `differentiate_expr(sum_node.body, var_name, (sum_idx,), Config(...))` |
| `stationarity.py:1130` | `differentiate_expr(sum_node.body, var_name, src_indices, Config(...))` |

**`bound_indices=` appears ZERO times in `stationarity.py`.** `differentiate_expr` accepts it as a keyword with a `frozenset()` default, so every one of these calls silently asserts *"nothing is bound"* — which is why Task 4's probe found `bound_indices=[]`. **The information was never destroyed; it was never passed.**

**Why this matters: it would make Task 4's refuted direction-2 predicate expressible.** With the binder threaded, `e ∈ bound_indices` separates the two cases *as Day 4 originally described them* — prolog's `gp` **is** the peeled sum's index (suppress), while ganges' `j` is the prod's own bound (fire).

**⚠ UNTESTED. This is a hypothesis with a located surface, not a result.** Three cautions, all earned this sprint: the `file:line` references above are **traced but not exercised**; threading a binder into the shared differentiation entry path is **exactly** the high-blast-radius shape the S36 leak lesson is about, so it needs the full-corpus gate; and this is the third consecutive P1 direction to look clean on inspection — Day 4's direction 2 and today's direction 1 both did too.

### 6.2 Direction B — relocate the rebind

Move the rebind to a stage that still holds the equation's free-index context. §3 shows the *rendering* is where consistency is lost, so B and the §3 mechanism point at the same region. **Not evaluated further today** — A is strictly cheaper and, if it works, makes B unnecessary.

### 6.3 What the owner is deciding

**The REPLAN stands regardless** — direction C is dead and P1 cannot land today. The open question is whether **Day 2 spends its ~9 h on direction A** rather than the schedule's next item.

**For:** it is three call sites, precisely located, and it revives a predicate that was only refuted *because of the missing plumbing*. **Against:** it is untested, it touches the shared entry path, and the plan's own discipline says exit early rather than nurse a track across days. **P1 is 0-bucket either way** — success is a lateral `pse −2 / mi +2`, no Solve or Match gain.

**Recommendation: bank it and hold.** Sprint 38 has no floor lever, P1 was never a KPI mover, and the P8 reallocation is already justified. Direction A is a strong opening for a *future* P1, and it is now cheap to start because the surface is named.

### 6.4 ✅ OWNER DECISION (2026-08-19): **HOLD**

**Adopted.** Direction A is **banked, not pursued in Sprint 38**. P1 stays REPLAN'd at 0 bucket, and its ~14 h is released.

**Consequences, recorded so they are not rediscovered:**

1. **Day 2 and Day 3 have no P1 content.** The schedule assigned them 9 h + 5 h for *"P1 `src/` land + full-corpus leak gate"* and *"P1 Phase-0 gate + bucket verdict"*. Both are void — there is nothing to land.
2. **The freed 14 h cannot simply move to P8**, which the REPLAN table names as the absorber: **P8 is gated by P7** (no candidate has a Phase-0 gate), and P7 is scheduled Days 9–10. Moving hours into a track that cannot start is exactly the phantom-capacity error this plan was written to avoid. **§6.5 states the options rather than silently re-planning.**
3. **Unknown 1.5 loses its window.** Day 3 was to re-compile dinam/indus/turkpow/clearlak *"while the fix is in the tree"*, and there is now no fix in the tree. **1.5 stays 🔍 INCOMPLETE for the sprint** and carries to whichever effort lands a `$149` fix — the same disposition Task 4 gave it, for the same reason.
4. **`ISSUE_1667`'s Phase-0 gate is not exercised**, so P1 contributes no firm landing under close rule 1. It is a **carryforward with a bounded next step**: direction A, at the three call sites named in §6.1.

### 6.5 What Days 2–3 should absorb — an owner call, with the honest options

**Pulling P7 forward is the only move that also unblocks something.** P7 gates P8, so starting it early is the one reallocation that converts freed hours into later capacity rather than parking them.

| option | effect | note |
|---|---|---|
| **Pull P7 forward to Days 2–3** ← *recommended* | P8 becomes startable earlier; the Days 9–10 P7 slot frees for P8 | P7 is **under-budgeted at 8–10 h against 43 issues** (Task 9), so extra hours are genuinely useful, not make-work |
| Pull P6a/P6b forward | harmless, but 6b already precedes its two dependents on Day 4 | buys no ordering |
| Extend P8 at the end | **blocked** — P8 cannot start before P7 | this is the trap |
| Leave Days 2–3 unfilled | honest, and costs 14 h of a 116 h sprint | acceptable if the owner prefers not to re-plan mid-sprint |

**No option is applied here.** Re-planning the sprint is not Day 1's authority, and the plan's §6 pre-registers where budget goes precisely so it is not improvised.

## 7. Reproduction

```bash
# The scratch patch: banked $149 rebind + residual assertion, at the
# symbolic_name_match branch of _diff_prod (src/ad/derivative_rules.py).
# Probe prints only when D1_PROBE_MODEL is set; it changes no value.

# §2.1 — totality: zero residual across 265 fires
for m in prolog camcge lmp2; do
  D1_PROBE_MODEL=$m .venv/bin/python -m src.cli data/gamslib/raw/$m.gms \
      -o /tmp/d1/probe/${m}_mcp.gms 2>/tmp/d1/probe/$m.log >/dev/null
  echo "$m fires=$(grep -c RESIDUAL /tmp/d1/probe/$m.log)" \
       "nonempty=$(grep RESIDUAL /tmp/d1/probe/$m.log | grep -cv 'ParamRef=\[\]  VarRef=\[\]')"
done

# §3 — prolog drifts -3 bytes; one line, stat_p(i)
diff data/gamslib/mcp/prolog_mcp.gms /tmp/d1/probe/prolog_mcp.gms

# §4 — ganges/gangesx, per model. Read GAMS's OWN total, never marker counts.
mkdir -p /tmp/d1/x && cd /tmp/d1/x
.venv/bin/python -m src.cli <repo>/data/gamslib/raw/ganges.gms --nlp-presolve -o ganges_mcp.gms
gams ganges_mcp.gms lo=0 errmsg=1
grep -E '^\*\*\*\* [0-9]+ ERROR\(S\)' ganges_mcp.lst
grep -c 'Remaining errors not printed' ganges_mcp.lst     # 2 -> markers undercount

# §6.1 — the binder is never passed
grep -c 'bound_indices=' src/kkt/stationarity.py           # 0
grep -n 'differentiate_expr(sum_node.body' src/kkt/stationarity.py

# working tree restored
md5 -q src/ad/derivative_rules.py                          # == pristine
```

---

**Document Status:** ✅ Complete — Sprint 38 Day 1. **🔶 REPLAN taken the same day.** **#1668 direction 1 is a NO-OP** (265 fires, zero residual — its premise is false); the asymmetry is manufactured **downstream** by positional re-symbolization under an alias, so **neither #1668 direction is implementable at the rebind site**. **Unknown 1.1: the `$149` component reproduces on current `main`** (199 → 178 errors, `$149` → 0, both models); the full four-fix `rc=0` claim is **not** re-established, and that is stated as a bounded gap. **P1's ~14 h → P8.** **Direction A is banked, located at three call sites, and untested.**
**Last Updated:** 2026-08-19 · **Owner:** Sprint 38 execution team
