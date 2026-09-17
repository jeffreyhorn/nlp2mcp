# P10 — the six P2-flagged models, TRIAGED (Sprint 39 Day 12)

**Measured at `3548a20b`** · GAMS **54.2.1** · every emitted line and every
source rule below read from the tree, not recalled.

`check_index_repeat_properties.py`'s **P2** ratchet holds **9 violations across
6 goldens**. The survey's framing was *"a repeated index inside an emitted
`$(...)` guard is manufactured unless the source declares it so"*. Measured
against each model's source, that framing is **half right**: there are **two
classes with different roots**, and the distinction decides the remedy.

## The two classes

| class | what the source says | what the emit does | effect |
|---|---|---|---|
| **A — MANUFACTURED** | the SYMBOL's domain keeps the two positions **DISTINCT** | emit substitutes the **same symbol into both** | **a coordinate is lost** — the reference reads the wrong cell. Often that cell is tautological, giving an identically **TRUE** or identically **FALSE** guard (turkpow, dinam); where the symbol is a data table it is simply the **wrong lookup** (egypt) |
| **B — DECLARATION-faithful, ASSIGNMENT-narrowing** | the SYMBOL — a **set OR a parameter** — is **declared** over the same set twice (legal GAMS: the full product) | emit reuses that declaration domain in an **assignment / guard** context, where GAMS reads it as the **DIAGONAL** | the statement covers only the diagonal |

⚠ **"SYMBOL", not "parameter" — the class spans BOTH kinds** (PR #1743 review;
an earlier revision of this table said *parameter* throughout). Measured in the
sources: `gussrisk`'s `covar(stocks,stocks)` is declared under `Parameter`, but
`nonsharp`'s `inter(col,col,stm)` is declared under **`Set`**. The
declaration-vs-assignment context error is identical for both, so a definition
naming only parameters is factually wrong for half the class and would send a
reader looking in the wrong declaration block.

**Class B is not a manufactured repeat** — the symbols came from the source's own
declaration. It is a *context* error: the same text means "full product" in a
declaration and "diagonal" in an assignment. P2 cannot tell them apart from the
emitted text alone, which is exactly the limitation recorded in
`check_index_repeat_properties.py`'s module docstring.

⚠ **CLASS A's EFFECT IS COORDINATE LOSS, NOT "TAUTOLOGICAL GUARD"** (PR #1743
review — an earlier revision of the table above said the guard *always* becomes
identically TRUE or FALSE, which its own `egypt` row contradicts). The tautology
is what coordinate loss produces when the symbol is an `ord`-style relation;
`egypt`'s `tranc` is a data **Table**, so the same substitution yields a wrong
*value* rather than a constant guard. Stating the narrower symptom as the class
definition would have made `egypt` look misclassified when it is not.

## Per-model findings

| model | emitted | source rule | evaluates to | class |
|---|---|---|---|---|
| **dinam** | `ts2(te,te)` | declared `ts2(te,tep)`; `ts2(te,tep) = 1$(ord(te) > ord(tep))` | `ord(te) > ord(te)` → **identically FALSE** | **A** |
| **egypt** ⚠ | `tranc(rp,rp)` | `Table tranc(r,rp)` | reads the **wrong coordinate** (`r` replaced by `rp`) | **A** |
| **turkpow** | `vs(v,v)` | declared `vs(t,v)`; `vs(t,v) = (ord(t) >= ord(v))` | `ord(v) >= ord(v)` → **identically TRUE** | **A** |
| **turkpow** | `vs(t__kkt1,t__kkt1)`, `vs(t__kkt2,t__kkt2)` | same | **identically TRUE** — and the minted alias went into **both** positions | **A** |
| **shale** ⚠ | `ts(tf,tf)` (×2, both in guards on `:344`) | declared `ts(tf,tf)`; `ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1` | `ord(tf) < ord(tf)` → **identically FALSE** | **B origin, A effect** |
| **gussrisk** | `covar(stocks,stocks)` | declared `covar(stocks,stocks)`; `covar(s,sp) = …` | NA-cleanup covers only the **diagonal** | **B** |
| **nonsharp** | `inter(col,col,stm)`, `inter(col__kkt1,col__kkt1,stm)` | declared `inter(col,col,stm)`; `inter(colp,col,stm) = no` | narrows to the **diagonal** of `col × col` | **B** |

⚠ **`egypt` and `shale` are license-gated** (`path_solve_license`), so any fix is
verifiable **by property and by golden, but NOT by a solve**.

## Why this matters, stated as effect rather than as a lint

An identically-TRUE guard is **inert** — it emits a term that should have been
conditional. An identically-FALSE guard **silently drops** a term that should
have been present. Neither produces a GAMS error, and `dinam`, `shale`,
`turkpow` and `egypt` are all `mcp_solve: failure` today for other reasons, so
**no currently-reported KPI is moved by any of these**. They are latent wrong
answers waiting behind other blockers, which is precisely why a ratchet rather
than a hard gate was the right shape.

## The shared root, and its relationship to P5

**Class A is the same defect family the P5 survey catalogues** — a symbol→position
step that resolves two distinct source positions onto one symbol. `turkpow` is
the clearest instance: the KKT alias minter produced `t__kkt1` and substituted it
into **both** coordinates of `vs`, where the source has `(t,v)`.

That makes Class A a **downstream symptom of the survey's sites**, not an
independent bug list — and it is why P5's `NEEDS A TEST` sites matter beyond
their own reach counts.

## Disposition

**No fix lands in Sprint 39, and the P2 baseline is unchanged at 9.** Each Class-A
fix is an emit change in `src/kkt` or `src/ad`, so each needs its own Phase-0
acceptance doc, golden regeneration and a re-solve — and for `egypt`/`shale` the
re-solve is unavailable. Landing a partial fix would move the ratchet without
being able to demonstrate correctness on two of the six.

**Carried to Sprint 40** as a classified work list: Class A first (`turkpow` is
the most tractable — the alias-minting site is named), Class B second (it needs
the declaration-vs-assignment context distinction, which is a larger change and
the one `check_index_repeat_properties.py` already records as unsolved from the
emitted text alone).
