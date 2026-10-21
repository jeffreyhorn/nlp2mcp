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
