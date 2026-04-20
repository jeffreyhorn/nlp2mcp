# Investigation — Parser Non-Determinism (#1283)

**Created:** 2026-04-20
**Sprint:** 25 (Prep Task 3)
**Issue:** [#1283](https://github.com/jeffreyhorn/nlp2mcp/issues/1283)
**In-tree doc:** [`../../../issues/ISSUE_1283_parser-non-deterministic-multi-row-label-table.md`](../../../issues/ISSUE_1283_parser-non-deterministic-multi-row-label-table.md)
**Related KU:** Sprint 24 KU-27 (Lark 1.1.9 vs 1.2+ grammar ambiguity — different bug, same "Earley ambiguity picks non-deterministically" family)

---

## Executive Summary

Root cause of #1283 is **Earley grammar ambiguity in the `table_row` / `simple_label` / `dotted_label` rule chain**, not dict/set iteration order in parser code. The GAMS grammar in [`src/gams/gams_grammar.lark`](../../../../src/gams/gams_grammar.lark) lets a bare `NUMBER` token be either a `table_value` (intended) or a `simple_label → dotted_label → NUMBER` (also grammatically valid). For a data row like `low.a 1 2 3`, two parses exist:

1. One `table_row` with `simple_label(low, a)` + 3 `table_value` tokens (the intended parse).
2. Four `table_row`s: `simple_label(low, a)` with 0 values, then each of `1`, `2`, `3` as its own zero-value `simple_label` row.

Both parses satisfy `table_row: table_row_label table_value*` because `table_value*` accepts zero. With `ambiguity="resolve"` in [`src/ir/parser.py`](../../../../src/ir/parser.py) line 163, Lark picks one alternative per parse — but the selection is hash-seed-dependent. Under 20 `PYTHONHASHSEED` values (0–19) the distribution is **7 correct : 13 corrupted (65% corruption rate)**, with exactly 2 distinct outputs.

The trigger is any `Table` block containing multi-row-label tuple expansions like `(low,medium,high).ynot`. The preprocessor ([`src/ir/preprocessor.py`](../../../../src/ir/preprocessor.py) `expand_tuple_only_table_rows`) expands the tuple label into per-label duplicate rows *before* parsing, so the actual Lark-visible input is two or three copies of `low.a 1 2 3`, `medium.a 1 2 3`, etc. — and each copy is individually ambiguous. Non-tuple tables aren't affected in practice because their row-label token is typically a text ID (not a bare NUMBER) and Lark's Earley heuristics reliably pick the longer-value parse.

**Scope:** 4 corpus models use multi-row-label tuple expansion — `chenery` (confirmed), `clearlak`, `indus`, `indus89`. Of these, `chenery` is the only currently-matching model; the others are already downstream-failing (`path_syntax_error` / `translate=success solve=failure`), so the bug is silent elsewhere but may be corrupting their IRs too.

**Recommended fix (Option D):** augment `_resolve_ambiguities()` in `src/ir/parser.py` to prefer the alternative that packs the most `table_value` children per `table_row` (the "greediest-value" parse), rather than Lark's default hash-dependent pick. Expected regression surface: low — this only affects `_ambig` nodes whose children include `table_row` trees, which is a narrow code path.

---

## Reliable Reproduction

_(originally §Section 1 — renamed to match the Task 3 verification grep in `SPRINT_25/PREP_PLAN.md`.)_

### Reproduction recipe

```bash
# Sweep 20 hash seeds and hash the output to count distinct parses
mkdir -p /tmp/task3-sweep && rm -f /tmp/task3-sweep/*.gms
for seed in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19; do
  PYTHONHASHSEED=$seed .venv/bin/python -m src.cli \
    data/gamslib/raw/chenery.gms \
    -o /tmp/task3-sweep/chenery_${seed}.gms --quiet > /dev/null 2>&1
done
# Cross-platform hashing (works on macOS and Linux):
cd /tmp/task3-sweep && for f in chenery_*.gms; do
  printf "%s  %s\n" "$(shasum -a 256 "$f" | cut -d' ' -f1)" "$f"
done | awk '{print $1}' | sort | uniq -c | sort -rn
# macOS quick-local variant (optional): replace shasum line with `md5 -q "$f"`
# Linux alternative: use `md5sum "$f" | cut -d' ' -f1`
```

### Observed results (20-seed sweep, 2026-04-20)

Output of the reproduction recipe (SHA-256 hashes):

```
13 008eab82075a6447d348be934055131b34fbc1d044dc3d2711bc3a86cee1aae9  (CORRUPTED — 65% of runs)
 7 e2feb2540bd3d8287be210c61fc50aa6e60f6f68280cf77fd016d5d7a14fb3e4  (CORRECT — 35% of runs)
```

For reference, the equivalent macOS `md5 -q` hashes are `da34fa8871ce5bcac46121f8d5973100` (corrupted) and `cf8dbf3fc53fd71e6e6d90f6a20cc58e` (correct).

Exactly **2 distinct outputs**. Corrupted seeds: `1, 2, 3, 5, 7, 8, 9, 10, 13, 14, 16, 17, 19` (13 seeds). Correct seeds: `0, 4, 6, 11, 12, 15, 18` (7 seeds).

Note: the issue doc's original "2 correct + 1 corrupted per 3 runs" observation is in the same ballpark as the actual 35%-correct / 65%-corrupted ratio on this 20-seed sweep (the issue-doc observation was itself sampled from an unknown hash-seed distribution, likely dominated by unset/default `PYTHONHASHSEED`). The direction of corruption majority may vary with Lark's internal tiebreak heuristics, but the existence of exactly 2 outputs is the stable property.

### Corruption signature (chenery.gms)

```
Correct:   low.ynot.'light-ind' 100, .'food+agr' 230, .'heavy-ind' 220, .services 450   (4 values)
Corrupted: low.ynot.'light-ind' 230, .'food+agr' 220, .'heavy-ind' 450                  (3 values, services dropped)
```

All three expansion rows (`low`, `medium`, `high`) exhibit the same shift; the `medium.p-elas` and `high.p-elas` rows (non-tuple-expanded) are unaffected.

---

## Section 2 — Minimum Reproducer

The bug reproduces with a **2-row-label × 3-column table with plain-ID columns** — no hyphens, no `+`, no CGE complexity:

```gams
Set
   lmh /low, medium/
   i   /c1, c2, c3/ ;

Table ddat(lmh,*,i)
                  c1   c2   c3
   (low,medium).a  1    2    3 ;

Parameter y(i);
y(i) = ddat("low","a",i);
Variables x(i), z;
Equations objdef, bal(i);
objdef.. z =e= sum(i, x(i));
bal(i).. x(i) =e= y(i);
Model m /all/;
Solve m minimizing z using nlp;
```

(Saved at `/tmp/task3-sweep/minrepro_2.gms` during this investigation.)

20-seed sweep on the minimum reproducer produces the same 7 correct : 13 corrupted distribution — confirming the trigger is independent of hyphens, plus signs, or column-name special characters. The prior hypothesis that `light-ind`/`food+agr` tokenization was involved is **ruled out**.

### Corruption signature (minimum reproducer)

```
Correct:   low.a.c1=1, low.a.c2=2, low.a.c3=3, medium.a.c1=1, medium.a.c2=2, medium.a.c3=3  (6 entries)
Corrupted: low.a.c1=3, medium.a.c1=2, medium.a.c2=3                                         (3 entries)
```

Three entries survive; three are dropped. The retained values are [3, 2, 3] — a non-trivial permutation (not simple shift-right), consistent with the column-alignment pass picking up a small subset of the tokens after some are mislabeled as row labels.

---

## Narrowed Root Cause

_(originally §Section 3 — renamed to match the Task 3 verification grep.)_

### 3.1 Grammar ambiguity

The relevant grammar rules ([`src/gams/gams_grammar.lark`](../../../../src/gams/gams_grammar.lark) lines 320–343):

```lark
table_row: table_row_label table_value*
table_row_label: "(" set_element_id_list ")" "." "(" ... ")"  -> tuple_cross_label
               | dotted_label "." "(" ... ")"                 -> tuple_suffix_expansion_label
               | "(" id_list ")" "." dotted_label             -> tuple_label
               | dotted_label                                  -> simple_label
dotted_label: (ID | STRING | NUMBER) ("." (ID | STRING | range_expr | NUMBER))*
table_value: NUMBER | ID | range_expr | negative_special | negative_number
```

**Ambiguity:** `dotted_label` accepts a bare `NUMBER`. Therefore `simple_label` (and the `table_row` that contains it) can match a bare `NUMBER`. Combined with `table_value*` allowing zero values, Earley finds multiple valid parses for any row like `low.a 1 2 3`.

### 3.2 Parse trees confirmed by probing

Running the real parser under two hash seeds and dumping all `table_row` children for the minimum reproducer produces:

**Seed=0 (CORRECT parse, 3 table_row nodes):**

```
table_row: simple_label(dotted_label(ID=c1)) + table_value(c2) + table_value(c3)
table_row: simple_label(dotted_label(ID=low, ID=a)) + table_value(1) + table_value(2) + table_value(3)
table_row: simple_label(dotted_label(ID=medium, ID=a)) + table_value(1) + table_value(2) + table_value(3)
```

**Seed=1 (CORRUPTED parse, 9 table_row nodes):**

```
table_row: simple_label(dotted_label(ID=c1)) + table_value(c2) + table_value(c3)
table_row: simple_label(dotted_label(ID=low, ID=a))            # <-- 0 values
table_row: simple_label(dotted_label(NUMBER=1))                 # <-- value mis-parsed as row label
table_row: simple_label(dotted_label(NUMBER=2))                 # <-- value mis-parsed as row label
table_row: simple_label(dotted_label(NUMBER=3))                 # <-- value mis-parsed as row label
table_row: simple_label(dotted_label(ID=medium, ID=a))          # <-- 0 values
table_row: simple_label(dotted_label(NUMBER=1))
table_row: simple_label(dotted_label(NUMBER=2))
table_row: simple_label(dotted_label(NUMBER=3))
```

Both parses are **grammatically valid**. Under `ambiguity="resolve"`, Lark picks one based on its internal precedence/tiebreak; the pick varies per hash seed.

### 3.3 Why `_handle_table_block` produces corrupted output, not an error

When the 9-row parse is selected, the downstream code ([`src/ir/parser.py`](../../../../src/ir/parser.py) `_handle_table_block`, lines 2108–2300) collects tokens from every `table_row.children`, and for every `simple_label` it marks the inner tokens as `row_label_token_ids` (line 2160). The NUMBER tokens `1 2 3` are marked as row-label tokens in this parse — so they're excluded from `table_value` matching. The column-by-position matching then has only 2 of the 3 values available per row (because one has already been consumed as the "row label"), producing the observed 3-entry corruption pattern.

The parser does **not** raise a validation error for this case because:
- The first `table_row` successfully produces a valid row label `(low, a)` → `low.a`.
- Subsequent `simple_label(NUMBER)` rows have `row_label = "1"`, `"2"`, `"3"` — harmless stringifications that don't trigger any domain checks.
- The column-position matching code silently works with whatever tokens remain.

### 3.4 Why the bug is hash-seed-dependent

`ambiguity="resolve"` in Lark 1.1.9 / 1.2.x uses rule priorities and earliest-start heuristics for tiebreak. When multiple valid `_ambig` alternatives have equal priority, Lark's internal data structures — which in current versions include hash-based sets/dicts in the Earley chart state — resolve the ambiguity in iteration order, and that order depends on Python's hash seed.

Empirically: the 7 correct : 13 corrupted split (i.e., 7:13 when stated "correct : corrupted", or equivalently 13:7 when stated "corrupted : correct") suggests Lark is picking one of two specific alternatives roughly uniformly across the ambiguous node; the exact 7:13 vs 10:10 distribution is a function of how `PYTHONHASHSEED=0..19` happens to partition Lark's internal iteration.

### 3.5 Relation to Sprint 24 KU-27

Sprint 24 KU-27 resolved a *different* Earley ambiguity (`/ all - eq1 /` in model subtraction) via defensive IR rewriting in `_extract_model_refs`. Same root-cause family ("Earley ambiguity + ambiguity=resolve + hash-seed-dependent tiebreak") but a different specific rule. The KU-27 fix was downstream-of-parser; a similar downstream-of-parser fix is one of the options for #1283 (see Option D below).

---

## Section 4 — Scope Survey (Corpus Audit)

`grep -lE '^\s*\([a-zA-Z_][a-zA-Z0-9_, ]*\)\.' data/gamslib/raw/*.gms` identifies **4 corpus models** with multi-row-label tuple patterns at table-row column position:

| Model | Pattern | Current pipeline state | Determinism |
|---|---|---|---|
| `chenery` | `(low,medium,high).ynot` + `(medium,high).gam` / `.xsi` | translate=success, solve=success, compare=**mismatch** | **Non-deterministic (65% corrupt)** — confirmed |
| `clearlak` | `(mar,apr).dry` | translate=success, solve=failure (path_syntax_error) | Likely affected — downstream failure masks it |
| `indus` | `(basmati,irri).(bullock,semi-mech)` and others | translate=success, solve=failure (path_syntax_error) | Likely affected — downstream failure masks it |
| `indus89` | Multiple, including 5-tuple cross-products | translate=None (pipeline never reached) | Likely affected — not currently in pipeline comparison |

**Key implication:** `chenery_mcp.gms` has been silently flipping between 2 outputs (one correct, one corrupt) on every pipeline run since Sprint 22 or earlier. The #1177 chenery `model_infeasible` investigation was debugging against an unstable baseline — consistent with Sprint 24 Day 13 Addendum's observation.

The three remaining models (`clearlak`, `indus`, `indus89`) are downstream-failing for *other* reasons, so the non-determinism is silent there. Once upstream fixes land in Sprint 25, those models may also exhibit the same flakiness unless #1283 is fixed first.

---

## Proposed Fix

_(originally §Section 5 — renamed to match the Task 3 verification grep.)_

### Option A — Narrow `dotted_label` to exclude bare NUMBER row labels

**Change:** modify the grammar so `simple_label` cannot resolve to a single `NUMBER`:

```lark
dotted_label: ID_OR_STRING ("." (ID | STRING | range_expr | NUMBER))*
            | NUMBER ("." (ID | STRING | range_expr | NUMBER))+   // NUMBER only at start if there's a suffix
```

**Expected regression surface:** **HIGH**. Issue #863 intentionally added NUMBER support to `dotted_label` to handle GAMS models with numeric element names (e.g., `9000011`). Disabling bare-NUMBER labels would break any model using numeric-only row labels.

**Verdict:** Not recommended.

### Option B — Add Lark rule priorities

**Change:** mark `simple_label` with a lower priority than `table_value` via Lark's `.N` priority notation:

```lark
table_row: table_row_label table_value*
simple_label.1: dotted_label
table_value.2: NUMBER | ID | range_expr | negative_special | negative_number
```

**Expected regression surface:** **MEDIUM**. Priorities in Lark's Earley parser are used for `ambiguity="resolve"` tiebreak but don't always cleanly disambiguate within a rule like `table_row: table_row_label table_value*` where both children are at the *same* position. Requires empirical validation across the corpus.

**Verdict:** Worth prototyping but uncertain.

### Option C — Disambiguate in the preprocessor

**Change:** extend [`src/ir/preprocessor.py`](../../../../src/ir/preprocessor.py) to rewrite each table-data-line before the parser sees it — e.g., inject a marker token after the row label so Lark can't parse the values as row labels. Requires defining a marker that's grammar-visible but not in the output IR.

**Expected regression surface:** **MEDIUM-HIGH**. The preprocessor already does line-joining and tuple expansion for table rows; adding a third rewrite stage risks interacting badly with existing preprocessor logic.

**Verdict:** Possible but increases preprocessor complexity.

### Option D — Post-parse disambiguation in `_resolve_ambiguities()` ⭐

**Change:** extend [`src/ir/parser.py`](../../../../src/ir/parser.py) `_resolve_ambiguities()` so that when an `_ambig` node's alternatives contain `table_row` trees, it picks the alternative that packs **the most `table_value` children into the fewest `table_row` nodes** (i.e., the "greediest-value" parse). Lines 166–225 already implement a pluggable "pick first alternative" policy; swapping that for a table-row-aware policy is localized.

```python
def _pick_alternative(ambig_node: Tree) -> Tree:
    """Prefer alternatives whose table_row nodes have the most table_value children."""
    def score(alt):
        # Count (table_value_count, -table_row_count) for tiebreak
        values = 0
        rows = 0
        for sub in alt.iter_subtrees() if hasattr(alt, "iter_subtrees") else []:
            if sub.data == "table_row":
                rows += 1
                values += sum(1 for c in sub.children
                              if isinstance(c, Tree) and c.data == "table_value")
        return (values, -rows)
    return max(ambig_node.children, key=score)
```

**Expected regression surface:** **LOW**. The policy only activates when `_ambig` nodes contain `table_row` children — which is the exact failure case. For all other `_ambig` nodes, existing "pick first" behavior is preserved. Matches the Sprint 24 KU-27 PR #1267 precedent (defensive fix at the IR layer, not the grammar layer).

**Verdict:** **RECOMMENDED.**

### Option E — Determinism regression test + PYTHONHASHSEED in CI

**Change:** regardless of which fix is chosen, add a determinism-guard test that runs the minimum reproducer under 5+ distinct `PYTHONHASHSEED` values and asserts byte-identical output. Wire `PYTHONHASHSEED=0` into `Makefile` test targets until the root cause is fixed. This is a **complement** to the actual fix, not a substitute — it catches future regressions.

**Expected regression surface:** NONE. Test-only addition.

**Verdict:** **REQUIRED alongside any chosen fix.**

---

## Section 6 — Cross-Reference to Sprint 25 KUs

| KU | Relation |
|---|---|
| **Unknown 2.1** (#1283 root cause) | Verified by §Section 3 of this doc: root cause is Earley ambiguity in `table_row` → `simple_label` → `dotted_label` allowing NUMBER. Not dict/set iteration order as initially hypothesized. |
| **Unknown 2.2** (affected corpus count) | Verified by §Section 4: 4 corpus models (chenery, clearlak, indus, indus89), not "at most 3" as originally guessed. |
| Sprint 24 **KU-27** (Lark disambiguation — PR #1267) | Same bug family; PR #1267's defensive post-parse IR rewrite is the precedent for Option D. |
| Sprint 24 **KU-28** (requirements.txt pinning) | Not directly related but worth checking: are CI's Lark version and local Lark version the same? If not, the bug may behave differently in CI vs local. Both environments use `lark==1.1.9` per `requirements.txt` (as of 2026-04-20), so this is not a contributing factor to the current observed behavior. |

---

## Section 7 — Sprint 25 Implementation Sketch (for Priority 2 / Task 6 planning)

**Day 1 (when Priority 2 begins):**

1. Land a determinism regression test first (Option E) that pins `PYTHONHASHSEED=0..9` and runs the minimum reproducer — this is a no-risk change that catches regressions on this class of bug going forward.
2. Implement Option D: extend `_resolve_ambiguities` with a table-row-aware scoring policy. ~30 lines of code + ~10 lines of unit test.
3. Re-run the 20-seed sweep against chenery and the minimum reproducer — expect byte-identical output across all seeds.
4. Run full test suite (`make test`) — expect 0 regressions given Option D's localized scope.
5. Re-run `scripts/gamslib/run_full_test.py --only-parse` against the 4 affected models — expect consistent parse trees.

**Estimated effort (actual fix):** 2–3 hours on top of this 2–3 hour investigation → ~5h total for #1283, matching the 4–6h estimate in ISSUE_1283.

**Blocker for Sprint 25:** Priority 2 (Emitter / Stationarity bug backlog) should land this fix **first** in Sprint 25, before any chenery-touching investigation or metric collection, to ensure all downstream metrics are trustworthy.

---

## Appendix A — Lark explicit-ambiguity probe (reproduction)

To confirm the ambiguity structure directly:

```python
from lark import Lark
from pathlib import Path
from src.ir.preprocessor import preprocess_gams_file

parser = Lark.open('src/gams/gams_grammar.lark', parser='earley',
                   start='start', maybe_placeholders=False, ambiguity='explicit')
src = preprocess_gams_file(Path('/tmp/task3-sweep/minrepro_2.gms'))
tree = parser.parse(src)

def count_ambig(node):
    if hasattr(node, 'data'):
        if node.data == '_ambig':
            return 1 + sum(count_ambig(c) for c in node.children)
        return sum(count_ambig(c) for c in node.children or [])
    return 0

print(f'_ambig nodes: {count_ambig(tree)}')  # Expect > 1
```

When run, produces a top-level `_ambig` with 8 alternatives, and nested `_ambig` nodes deeper in the table_block subtree — confirming Lark's Earley parser legitimately sees multiple valid parses.

## Appendix B — Probing the selected table_rows under different seeds (reproduction)

```python
import sys; sys.setrecursionlimit(50000)
from lark import Token, Tree
from pathlib import Path
from src.ir.parser import _build_lark, _resolve_ambiguities
from src.ir.preprocessor import preprocess_gams_file

parser = _build_lark()
src = preprocess_gams_file(Path('/tmp/task3-sweep/minrepro_2.gms'))
raw_tree = parser.parse(src)
tree = _resolve_ambiguities(raw_tree)

def describe(node, depth=0):
    prefix = ' ' * (depth*2)
    if isinstance(node, Token):
        return f'{prefix}{node.type}={node!r}'
    return '\n'.join([f'{prefix}{node.data}'] + [describe(c, depth+1) for c in node.children])

for node in tree.iter_subtrees_topdown():
    if node.data == 'table_row':
        print('----table_row----')
        print(describe(node))
```

Run under `PYTHONHASHSEED=0 python -c '<above>'` → 3 table_rows.
Run under `PYTHONHASHSEED=1 python -c '<above>'` → 9 table_rows.
