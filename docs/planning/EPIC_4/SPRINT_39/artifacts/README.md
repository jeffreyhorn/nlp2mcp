# Task 7 measurement scripts

Every figure in `../POSITIONAL_DOMAIN_SURVEY.md` was produced by one of these.
They are committed so the survey is **reproducible from the repo** rather than
from prose — a review of PR #1718 correctly pointed out that the original
evidence lines pointed at `/tmp`, which no other contributor and no CI run can
reach.

**These are one-off prep measurement scripts, not maintained tooling.** They are
outside the quality gate's scope (`make lint`/`typecheck` cover `src/` and
`tests/`). If the P2 property graduates into a gate — the survey's first
recommendation to P5 — that lands as real code under `scripts/`, reviewed on its
own terms. Nothing here should be imported by product code.

Run **from the repo root**. All write into `$OUT` (default `/tmp/s39t7`).

| script | produces | runtime |
|---|---|---|
| `scan.py` | the raw shape population — 173 subscripted-domain, 33 zip-against-a-domain | seconds |
| `classify.py` | the 21 primary sites, by shape (K2–K6) | seconds |
| `prescan.py` | source-level repeated-domain candidates → `$OUT/prescan.json` | seconds |
| `census.py` | IR census over all 219 models → `$OUT/census.json` | **~45 min** |
| `kinds.py` | per-kind confirmation for the prescan candidates → `$OUT/kinds.json` | ~20 min |
| `reach.py` | blast radius by `sys.settrace` → `$OUT/reach.json` | ~25 min |
| `mktable.py` | §2's catalog table (needs `reach.json`) | seconds |
| `property2.py` | P1 and P2 over every committed golden | ~2 s |
| `mutation_controls.py` | **the controls behind §5** — exits non-zero if either property is vacuous | ~30 s |

**The controls earn their keep.** During PR #1718 review the repeat matcher was
generalised from `name(x,x)` to any arity; the rewrite silently wrote a literal
backspace into the compiled pattern, so P2 matched nothing. `mutation_controls.py`
failed immediately with `P2 control -- elec pre-fix 0 []`. A green corpus run
would have looked like "no violations" and shipped.

`mutation_controls.py` is the one to run first. It re-derives the claims the
survey actually rests on:

```
P1 control -- tricp with #1062 disabled : 4 violation(s) [...]
P1 live    -- 193 goldens, 3100 heads : 0 violation(s)
P2 control -- elec pre-fix 1 ['ut(i,i)'] / today 0
ALL CONTROLS PASS
```

**One environment dependency.** `mutation_controls.py`'s P2 control needs the
pre-fix elec golden, which it reads with `git show 82b91c94^:...`. That is
unavailable in a **shallow clone** (CI checkouts default to depth 1) or an
archive export. It no longer dies with a raw `CalledProcessError`: it prints the
cause, the fix (`git fetch --unshallow`, or `fetch-depth: 0`), and a note that
the P1 control needs no history and its result still stands. Verified against a
real `--depth 1` clone, not simulated.

**Two fidelity notes.** The committed copies differ from the run copies only in
that the output directory is parameterised as `$OUT`. And `census.py`/`kinds.py`
carry a per-model `SIGALRM` timeout — 41 of 219 models do not parse, which is
why the per-kind figures in §4 are lower bounds rather than exact counts.
