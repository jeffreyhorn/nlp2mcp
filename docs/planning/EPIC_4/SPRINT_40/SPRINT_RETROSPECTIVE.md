# Sprint 40 — Retrospective

**Closed 2026-11-07 at `ca83e884`.** Figures: `SPRINT_LOG.md` §*Day 13*. Every
number below is derived there and quoted here with its commit; none is recalled.

## 1. What the sprint actually did

**It unlocked the license, measured a long-hidden slice of the corpus, and
reported it honestly.** `path_solve_license` 11 → 0, once; and the 11 cohort
rows redistributed by identity, not by headline — **3 solve, 1 matches
(turkey — floor +1), 2 at `path_solve_terminated` (ferts, tabora — cold MCP
aborts with `EXECERROR 36` on empty-equation-but-unfixed multiplier pairs,
per #1767), 5 proven infeasible under license (egypt, robot, shale, tfordy,
tricp), 1 stale-by-design (sroute, Day 11)**. The numbers on the headline rose
(Solve 111 → 114, Match 95 → 96, floor 75 → 76) — but C3 reports them as
*license-unlocked, not recovered*, in the plan's pre-written sentence, because
none of those moves is a fix: every emit is byte-identical to its committed
golden. Only the ability to run them changed.

**Eight of the nine pre-registered close rules (C1, C2, C3, C4, C5, C6, C8, C9)
are MET; C7 is UNMET not VOID.** C7's precondition held — P6's E5/E6 started on
Day 9 and was re-scoped on Day 10 — but sarf did not produce a byte-stable
golden at the gate threshold, so Translate stays 135. **Five of nine take no
precondition**, and all five are MET. That is the discipline working: rules that
guard correctness and reporting cannot be voided at all.

**Firm landings, all three-gated (C2):** P1 (schema 3.1.0 + hosted licensed CI
+ corpus re-base), P2 (cohort batch persist), P3 (9 admitted by rule), P7
(#1755), P4 (#1782 Pattern-C binder rewrite, Days 6–7, P2 ratchet 11 → 6), P4
(#1787 + #1790, Day 8, P2 ratchet 6 → 3), P6 (#1794 ReferencedInstanceFilter E1–E4 + E7/E8 byte-identical),
tfordy's Day-10 persist (owner decision), P9a (#1799 own-infeasible → mismatch),
P10a–e (five process items). **Fourteen distinct landings.** The one emit-moving
headline change is turkey's +1 floor, which the Sprint 35 Day 6 fix (`95ba01ea`)
earned and the Sprint 40 license actually tested — a credit that could not be
booked before.

**Prep refuted 48 % of its own unknowns** (14 of 29 — vs S39's 63 %, S38's
32 %). The lower refutation rate is a composition effect, not a worsening: 11
of S40's 29 unknowns were about *the license* (effective license, discriminator,
isolation, writer list, every cohort fingerprint), and prep resolved those
without needing to refute an assumption — the measurement itself was
unprecedented. Keep the number anyway; a prep that measures more is a prep that
knows more.

## 2. The thing worth generalising: a plan's biggest bet pays off when prep is routed to the measurement that will replace it

**The sprint's single most important Day-0 decision was not a technical one.**
Prep Task 6 answered three owner questions — Floor B (provenance-ledger
counting), Corpus A (admit-by-rule), CI B (hosted, access code per-run OK) — and
pinned them at `b44344a2`. Every rule in §5 of `PLAN.md` was then written
*against those answers*, so every one of nine rules at close could be read with
its precondition traced to a single commit. **That is the mechanism C9 depends
on:** its definition includes "the affected set is derived and pinned by
identity when P9a starts" rather than "prep's 7", because by Day 11 the set
*must* be derived — P2 by then has persisted the cohort, Task 7 has measured
five own-infeasible MCPs there, and prep's enumeration is stale by construction.

**The plan anticipated this and wrote the rule accordingly.** C9's close-day
measurement was `k = 12`, not prep's 7; the sprint read it and reported it.
That is a rule that aged well.

**C1 is the companion example.** Read literally, "`path_solve_terminated`
maintains 0" would report a first measurement as a regression. Task 7 found
ferts and tabora at `path_solve_terminated` *before* P2 ran — and the rule was
amended to name its population, pinned by identity. Three rows now sit there at
close (ferts, tabora, minsurf), and that is reported as "0 outside, 3 inside,
named individually", not as "+3 regression". **Prep found two in-scope
populations where a terse rule would have mis-reported both.**

**The one place the plan's bet lost is worth naming too.** C7 bet that P6 could
produce a sarf golden at ≤ 300 s if E5/E6 started. It started; the goal missed,
because the cost was not `_diff_sum`'s algorithm but its *input shape* — a
51,792-tuple left-deep OR guard built by `_build_tuple_or_guard` for a
non-Cartesian subset of task instances. **A rule can be pre-registered against
the right track and still miss the right layer.** That is the S38 D11/D12
lesson reappearing in a new costume — the layer named in the gate, however
carefully, is a hypothesis until measurement.

## 3. The attribution carry (sroute), and why a known-stale row is better than a wrong-written one

**sroute was the sprint's one deliberate non-persist.** Day 8's #1787
multi-reference fix made its cold emit solve; Day 10 CK2 confirmed it (re-solve
→ presolve match); the Day-10 CK2 log logged it; **Day 11 P9a deliberately did
not persist sroute**, because its MCP produces an own `MODEL STATUS 1 Optimal`
that matches the embedded NLP's answer — the S38 D9 `weapons` spurious-match
shape. The right verification is `check_mcp_solve_attribution`, not another
re-persist.

**The cost of this discipline is a known stale row at close:** the DB has
sroute as `model_infeasible + not_tested`, the live licensed cohort run (CI
42399418829) produces MS 1 Optimal. That delta is uncomfortable to read, and
reporting it as *known* rather than *persisted* is the right call. S38 D10
booked `weapons` as a match without the attribution; S39 D10 had to correct
Match 96 → 95; **this sprint is trying not to pay that bill a second time.**

**The general shape:** a cohort row whose MCP produces an own optimal that
matches the embedded NLP solution is **under-verified by presolve-match
alone**. Reading the value of `tetd.l` alone does not distinguish: a
successfully completed MCP can legitimately retain the warm-started value.
**The discriminator is `Attribution.mcp_succeeded`** — ownership (the
*last* summary from `self.mcp_summaries`, our emitted MCP), solver completion
(`solver_status == _NORMAL_COMPLETION`, with the `not aborted` / `not
abort_ambiguous` safety predicates), and model status (`model_status in
_SUCCESS_MODEL_STATUS`), as implemented in
`scripts/sprint_audit/check_mcp_solve_attribution.py:352–384` (the predicate
itself; the ownership selection is `mcp_summaries` at `:316–319`).
That is the attribution-check that Sprint 41 owes.

## 4. The index-repeat ratchet, and why 9 → 3 is a correctness improvement counted as process

**The P2 baseline moved 9 → 11 → 9 → 6 → 3 across four persists: Day 3
grew it +2 as egypt/shale presolve copies were persisted (`f1771435`); Day
6/7 P4 #1782's Pattern-C binder rewrite hoisted turkpow × 3 and shale ×
2; Day 8 P4 #1787/#1790 hoisted egypt × 2 and gussrisk. −6 net, across
four distinct models.** None of those moved Solve or Match at close; the
ratchet is why. These were models whose stationarity emit used a repeated
controlling index (a guard like `$ord(v) > ord(v)`, which is tautologically
false), and the right counter to "a quiet wrong answer" is a *gate*, not
an ad-hoc fix. **P4 wrote the rewrite so that at every Pattern-C
admission, BEFORE re-symbolisation, binders are mapped to their
variable-position names and the eq label is replaced with E\*.** The
remaining 3 entries at close are **dinam's `ts2(te,te)`** and **nonsharp's
two `inter(…)` references** (`inter(col,col,stm)`, `inter(col__kkt1,col__kkt1,stm)`);
**nonsharp was NOT hoisted this sprint** — it is a refused MINLP, so
regeneration cannot move its golden, and dinam has a separate open
diagnosis.

**The P2 gate is why this counts.** `make check-index-repeats` runs on every
PR (enforced in CI since S38 D3); it would have refused a fix that moved two
goldens and broke one. The gate's baseline carries the real violations at a
pinned count, and the rule is "a fix means `--update-baseline` in the same
commit". Six distinct emit defects were silenced structurally, in order, by
one Phase-0 rewrite — and the ratchet is what pinned the discipline rather
than a single PR's green.

## 5. What went well

- **The retest ran cleanly.** check-goldens unqualified-and-alone, with
  `--fail-on-unverified` from P10c, reported **200 in-scope goldens** (out of 207
  discovered; 7 are allowlisted) **all clean** (↑ 186 at S39 close);
  determinism ×3 `PYTHONHASHSEED` {0, 1, 42}: PASS ×3 (same 200 goldens
  byte-identical under every seed); make test 5,806 passed;
  check-index-repeats PASS (P1 0 / 3,370, P2 3 = baseline 3);
  check-doc-figures clean.
- **P10 is a sprint of its own in miniature.** Five process items landed —
  anchor resolver, `**Positive control:**` as an added-only requirement,
  `--fail-on-unverified`, `--text FILE`, Review-Round Rules in CONTRIBUTING —
  and each has a fail-before test and a specific prior failure it would have
  caught. Together they make the pre-registration discipline that the
  nine-rule close relied on *durable*, not conventional.
- **The gate caught its own regressions.** PR #1801 ran four review rounds;
  three of them were the parity test itself hardening against classes of
  bullet marker (tabs, `*`, `+`), and the fourth was the Makefile apostrophe
  escape. Each round was a small, measurable step, and the extractor is now
  more thorough than the hand-pinned four-phrase check it replaced.
- **The licensed CI held isolation, not just detection.** 10 PR workflow
  runs this sprint, every one `edition=demo`; across the sprint window
  (2026-10-18 → 2026-11-07, derived from `gh run list --workflow=licensed-solve.yml`)
  the `gams-licensed` environment saw **13 `main`-push runs and 19 nightly
  `schedule` runs on `main`**, every one `edition=licensed` with the
  positive control hit and no `USER:` line. The `gams-licensed`
  environment's branch-policy + per-run activation design works as designed,
  measured.

## 6. What did not

- **sarf's +1 Translate missed again** (S37, S38, S40 — three unfulfilled
  bets; **S39 was a Day-0 deliberate re-scope to branch B**, per
  SPRINT_39/PLAN.md:11, which made C6 VOID and scheduled no sarf
  implementation — it does not count as a missed sprint, and conflating
  VOID with UNMET would collapse the distinction this closeout depends
  on). The cost model was wrong three sprints running: S38 said
  `_diff_sum` 2.9 % self (correct, irrelevant); Day 9 said one unfiltered
  loop (correct, insufficient); Day 10 said the guard algorithm (correct,
  insufficient again). It is now re-scoped to three filed issues
  (#1795/#1796/#1797), each with a specific fix surface, and there is no
  Translate claim in the headline.
- **P5 #1789 reached a fixture target and was banked.** The lead/lag
  fixtures hit 68.546 = NLP on the prototype — a controlled-input result,
  not a corpus match (and the prototype's quoted-literal lift attempt was
  an independent unresolved defect); then robot and rocket moved BACKWARD
  to `path_solve_terminated`, lnts `stat_step` residual got worse, glider's
  subset domain wrong. The diff is a durable commit (`f57bc1d7` on
  `banked/1789-scalar-offset`), the three mechanisms are named on #1789, and
  it is Sprint 41 work — not because the fix was wrong, but because an
  honest bank beats a dishonest ship.
- **Two stale DB rows at close** (sroute, abel). Both are known, both are
  explained, both are carries — but a clean close does not have known-stale
  rows, and the `check_mcp_solve_attribution` verification that sroute needs
  is the Sprint 41 item that closes them.

## 7. Process changes to carry into Sprint 41 prep

1. **Route the first licensed full run to a route that lets it persist.** The
   Day-2 RT this sprint was deliberately not persisted (the throwaway
   worktree at `/tmp/rt/wt`); the known-item carries (sroute/abel) are the
   cost of that choice. Decide at prep whether the opening-day licensed run
   (whatever shape it takes in Sprint 41) writes rows it measures.
2. **Pin every cohort row's intended outcome at prep, derived from Task 7's
   measurement.** The sprint's one close-day surprise was not technical: it
   was finding that the licensed CI run showed sroute MS 1 Optimal while the
   DB had `model_infeasible` from prep. Task 7 saw the fingerprint; the
   intended destination was never pinned. Pin it, so that a stale row at
   close is a decision, not a discovery.
3. **When a fix touches shared machinery, prove it is byte-identical on the
   unqualified scope, and name the rows that the author expects to move.**
   PR #1794 (P6 filter) did this exactly right: 200 goldens byte-identical,
   fixture hashes × 4 unchanged, "no sarf set name collides with a label"
   verified on the inequality Jacobian's 158,666 differentiations. Three
   sprints of sarf regressions were avoided by that discipline.
4. **A rule that names a precondition that always holds is not pre-registered,
   it is just a rule.** C1, C2, C5, C6, C8 have no precondition; five of
   nine rules are "at every sprint close". Move the ones that keep reaching
   "precondition held" into the always-on list; a precondition that cannot
   fail is naming documentation discipline, not a bet.
