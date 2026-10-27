# ISSUE #1778 — stationarity: an equation whose domain index is absent from its body garbles its multiplier aggregation (`nu_e(i)$(ord(i)=k)`) — silent wrong answer

**GitHub:** [#1778](https://github.com/jeffreyhorn/nlp2mcp/issues/1778) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 5 (2026-10-20), found while verifying #1755, not fixed in place

**Found by:** Sprint 40 Day 5, while verifying the #1755 fix (P7) · **Measured at:** `main` `abc82d30` (pre-existing: byte-identical on an untouched `main` worktree) · **Layer:** stationarity assembly (KKT), not traced yet

## Minimal reproducer (a silent wrong answer)

```gams
Set i / i1*i3 /;
Alias (i,j);
Variable tsam(i,j), z;
Equation e(j), obj;
e(j).. sum(i, tsam(i,'i1')) =e= 1;
obj.. z =e= sum((i,j), sqr(tsam(i,j)));
Model m / all /;
solve m using nlp minimizing z;
```

| | result |
|---|---|
| NLP | **0.3333** |
| emitted MCP (PATH) | MS 1 at **0.375** — a wrong answer, booked as a solve |

The emitted row:

```gams
stat_tsam(i,j).. 2 * tsam(i,j) + nu_e(i)$(sameas(j, 'i1'))
  + (nu_e(i)$(ord(i) = 1))$((sameas(i, 'i1') or sameas(i, 'i2')) and sameas(j, 'i1'))
  + (nu_e(i)$(ord(i) = 2))$(sameas(i, 'i1') and sameas(j, 'i1'))
  + (nu_e(i)$(ord(i) = 1))$((sameas(i, 'i2') or sameas(i, 'i3')) and sameas(j, 'i1'))
  + (nu_e(i)$(ord(i) = 2))$(sameas(i, 'i3') and sameas(j, 'i1')) =E= 0;
```

**Hand-derived:** `e(j')`'s body does not depend on `j'`, so `∂ e(j') / ∂ tsam(a,'i1') = 1` for **every** `j'`. The correct row is `2*tsam(i,j) + (sum(j', nu_e(j')))$(sameas(j,'i1')) =E= 0`.

At `(i1,i1)` the emitted row gives `2*tsam + 2*nu_e(i1)`, not `nu_e(i1)+nu_e(i2)+nu_e(i3)`: one multiplier is doubled and two are missing.

## The shape

- The equation's **domain index `j` is absent from its body**, and the variable's position is over the **same (aliased) set** as the equation domain.
- The control `e(j).. sum(i, x(i)) =e= 1` with `x(i)` (no shared position) emits the correct `sum(j, nu_e(j))`.
- ⚠ **Hypothesis, not traced:** the guard `nu_e(i)$(ord(i) = k)` beside a multiplier with **no offset** looks like the **phantom-IndexOffset family** (#1381; silent members such as dyncge, #1714). The pattern is an `ord(...)=k` guard whose `nu_X(idx±k)` offset is lost. If confirmed, it belongs with that family.

## Relation to #1755

- The #1755 fix (Sprint 40 P7) makes `diagsum(j).. sum(i, tsam(i,i)) =e= 1` differentiate correctly (1 on the diagonal for every `j`). Its stationarity row then shows **this** defect: `nu_diagsum` appears only on the diagonal, as it should, but with the same garbled aggregation.
- #1755's scalar variant (no equation domain) is unaffected and solves to 0.3333.
- **This defect is independent of #1755:** the reproducer above has no repeated binder and is byte-identical before and after the fix.

## Corpus scope

`grep -E '(nu|lam)_\w+\([^)]*\)\$\(ord\(\w+\) = [0-9]+\)'` over the committed goldens finds **0** files at `abc82d30`. The positive control holds: the same pattern matches this reproducer's emit. So the shape is **latent in the corpus today**. ⚠ It becomes reachable wherever a fix newly references such a multiplier, as #1755's does for `diagsum(j)`.

## First step

Trace where `stat_tsam`'s cross-instance terms for `e(j')` are built (the stationarity layer, `_add_indexed_jacobian_terms` or its offset path), and check whether an `IndexOffset` is formed and then dropped. Then grep the goldens for `nu_\w+\((\w+)\)\$\(ord\(\1\) = \d+\)`: a multiplier indexed by the bare index beside an `ord(...)=k` guard.

**Not fixed in place.**

## Two more reproducers (Sprint 40 Day 5, PR #1779 review round 3)


After #1755's round-3 fix, AD returns the correct per-instance derivative with each layout's own binding: `act('i1')` at `w(i1,i1,i1,i1)` and `act('i2')` at `w(i1,i1,i2,i2)` (instrumented in the pipeline). **The stationarity row then generalizes both to `act(i)`**, the variable's FIRST domain position, although the binder's value sits at positions 3–4:

```gams
Set i / i1*i3 /;  Alias (i,j,k,l);
Parameter act(i) / i2 1 /;
Variable w(i,j,k,l), z;  Equation e, obj;
e.. sum(i$act(i), w('i1','i1',i,i)) =e= 1;                     * cond1
* e.. sum(i$act(i), w(i,i,'i2','i2') + w('i1','i1',i,i)) =e= 1;  * cond2, with act / i1 1 /
obj.. z =e= sum((i,j,k,l), sqr(w(i,j,k,l)));
Model m / all /;  solve m using nlp minimizing z;
```

| | NLP | emitted MCP |
|---|---|---|
| cond1 | 1.0 | **aborts**: `act(i)` is tested at `i = i1` (0), so `nu_e` drops from every row and `e.nu_e` is unmatched (`EXECERROR = 1`) |
| cond2 | 0.5 | MS 1 at **0.667**, a silent wrong answer |

- Both emits are **identical before and after** #1755's round-3 AD fix. The binding is lost in the stationarity generalization, not in AD.
- Like this issue's `nu_e(i)$(ord(i)=k)`, it is concrete→symbolic index mapping over aliased positions. The root may be shared; unverified.
- Latent in the corpus: the #1779 leak gate is byte-identical.

## Another reproducer: an outer binder on the first coordinate (Sprint 40 Day 5, PR #1779 review round 11)


```gams
Set i / i1, i2 /;  Alias (i,j);  Set ii(i);  ii(i) = yes$(ord(i) = 1);
Variable x(i,j), z;  Equation obj;
obj.. z =e= sum(i, sum(ii, sqr(x(ii,i) - 1))) + sum((i,j), sqr(x(i,j)));
Model m / all /;  solve m using nlp minimizing z;
```

| | row | MCP |
|---|---|---|
| NLP | | **1.0** |
| `main` | `stat_x(i,j).. 2 * x(j,j) =E= 0;` | 2.000 (also loses the #1755 term) |
| #1779 | `((2*(x(j,j) - 1))$(ii(j)) + 2*x(j,j))$(sameas(j,'i1')) + …` | 1.500 |

- The AD derivative is now correct per instance (the guard is `ii('i1')` at `x('i1','i2')`).
- The row's variable references and guard are mapped to `j` in BOTH positions. This is the same element-to-coordinate generalization over aliased positions as this issue's `nu_e(i)$(ord(i)=k)`, and the round-3 `act(i)` cases.

## Mixed bound + independent references (Sprint 40 Day 6, PR #1783 review round 2)


```gams
Set t / t1*t3 /;  Alias (t,v);  Variable z(v,t), obj;  Equation e(t), defobj;
e(t).. z('t1',t) + z('t1','t1') =e= ord(t);                 * shape A, NLP 8.75
* shape B (t / t1*t5 /, w(t) = ord(t)):  e(t).. 2*z('t3',t) - z('t2','t4') =e= w(t);   NLP 7.5
defobj.. obj =e= sum((v,t), sqr(z(v,t)));
```

| version | shape A | shape B |
|---|---|---|
| `main` | MCP fails (no model status) | fails |
| union reference binding (PR #1783 first revision) | 8.750 ✓ | **37.75, a silent wrong answer** |
| strict reference binding (as merged in #1783) | fails | fails |

- One reference binds the equation index (`z(…,t)`); another is a FIXED cell independent of it (`z('t1','t1')`, `z('t2','t4')`). Every equation row contributes to the fixed cell, so its stationarity term must be `sum(t', coef·nu_e(t'))`.
- The stationarity generalization has no way to express that. The union binding's success on shape A was the offset grouping happening to line up; on shape B the fixed cell took the bound reference's coefficient.
- **#1783 keeps the strict rule:** it never infers a binding from a reference that does not involve the index, and it matches `main`. The general fix belongs here, with the same absent-index logic turkpow's `stat_ht` needs (Sprint 40 Day 7).

## Another reproducer: labels shared across INDEPENDENT sets (Sprint 40 Day 7, PR #1788 review round 5)

```gams
Set i / a, b /, k / a /;
Alias (i,v);
Parameter c(i) / a 1, b 2 /;
Positive Variable x(k,v);
Variable obj;
Equation e(i), defobj;
e(i).. sum((k,v)$(ord(i) > 0), x(k,v)) =g= ord(i);
defobj.. obj =e= sum((k,v), c(v)*sqr(x(k,v)));
Model mm / all /;
solve mm using nlp minimizing obj;
```

On `main` (and on PR #1788, which deliberately falls back to `main`'s path here):

```
stat_x(k,v).. 2 * c(k) * x(k,k) + ((-1) * 1$(ord(v) > 0)) * lam_e(v) + (((((-1) * 1$(ord(v) > 0)) * lam_e(v+1))…$(ord(k) = 1))$(sameas(v, 'a')) + … =E= 0;
```

The MCP does not solve; the NLP gives 2.6667.

- **The cause:** the label `a` belongs to both `k` and `i`/`v`, so concrete → symbolic mapping cannot tell them apart. The gradient gives `c(k)` / `x(k,k)`, and the Jacobian gives phantom `lam_e(v±1)$(ord(k) = 1)` offsets.
- **Why PR #1788 does not apply its binder rewrite:** it renames the representative's eq label everywhere, which is sound only when that label is not also a variable label, and here no entry qualifies. So it withdraws the admission before consolidation.
- Same concrete → symbolic family as this issue and #1785.

## More mixed direct + summed references (Sprint 40 Day 7, PR #1788 review round 6)

The equation index appears directly AND inside a sum over a related set, so the summed contribution's cross-equation terms are wrong on `main`, and on PR #1788, which keeps `main`'s path for these on purpose:

```gams
* (a) subset t(tf), NLP 3.8221, MCP 85.953
Set tf / 1*5 /, t(tf) / 2*5 /;  Alias (tf,tfp);
Set ts(tf,tfp);  ts(tf,tfp)$(ord(tfp) < ord(tf)) = yes;
Variable x(tf), obj;  Equation e(tf), defobj;
e(t).. x(t) =e= 0.5*sum(tf$ts(t,tf), x(tf)) + 1;
defobj.. obj =e= sum(tf, ord(tf)*sqr(x(tf)));
```

`main` emits `stat_x(tf).. 2*ord(tf)*x(tf) + ((-1)*(0.5*1$(ts(tf,tf))))*nu_e(tf)$(t(tf)) + nu_e(tf)$(t(tf))`. Only the diagonal survives, and `ts(tf,tf)` is always 0.

```gams
* (b) a later binder, NLP 12.8859, MCP 28.0
e(t).. h('m1',t) + 0.5*sum((m,tf)$ts(t,tf), h(m,tf)) =g= ord(t);    * h(m,tf), m / m1*m2 /
```

`main` emits phantom `lam_e(tf+k)$(ord(m) = k)` offsets, and the #1110 multi-pattern correction is skipped (a UserWarning).
