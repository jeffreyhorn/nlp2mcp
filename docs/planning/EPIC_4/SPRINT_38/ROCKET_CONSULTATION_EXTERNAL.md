# PATH convergence on a discretized optimal-control MCP (Goddard rocket)

**Prepared for:** Michael Ferris, Steven Dirkse · **Date:** 2026-08-26 · **Status: SENT 2026-08-26** (tracked on issue #1462)
**Toolchain:** GAMS **54.2.1** / PATH **5.2.01** · all figures below measured on this toolchain unless marked otherwise.

---

## 1. Context

`nlp2mcp` is an open-source tool that translates GAMS NLP models into MCPs by emitting the KKT stationarity and complementarity conditions, then solves them with PATH. It is benchmarked against the GAMSLib corpus (219 models; 142 convex candidates).

`rocket` — the Goddard rocket from COPS, **GAMSLib sequence 319** — is the one model that resists every lever reachable from the emitter. We would value your guidance on it.

---

## 2. The failure

The MCP is emitted with an embedded warm start: the original NLP is solved inside the generated file, and its solution initialises the MCP. Both solves appear in one listing.

| | result |
|---|---|
| Embedded NLP | **MODEL STATUS 2** Locally Optimal, 20 iterations |
| Generated MCP | **MODEL STATUS 5** Locally Infeasible, **9,241 iterations**, `SOLVER STATUS 1 Normal Completion`, 0 evaluation errors |
| Size | 969 rows/cols, 4,491 non-zeros, 0.48 % dense |

PATH runs to completion and reports local infeasibility — it does not abort. Its own final statistics:

```
INITIAL JACOBIAN NORM STATISTICS
Maximum Row Norm. . . . . . . .  4.8909e+02 eqn: (stat_ht(h7))
Minimum Row Norm. . . . . . . .  1.3401e-02 eqn: (stat_t(h6))

FINAL STATISTICS
Inf-Norm of Complementarity . .  4.8575e-02 eqn: (stat_step)
Inf-Norm of Normal Map. . . . .  6.1601e-02 eqn: (stat_d(h37))
Inf-Norm of Fischer Function. .  9.3636e-02 eqn: (stat_step)
Inf-Norm of Grad Fischer Fcn. .  4.1033e+00 eqn: (stat_ht(h15))
```

The residual concentrates on **`stat_step`** — the time-step row of the discretization — under three of the four norms.

---

## 3. Evidence the KKT encoding itself is correct

Before asking about solver behaviour we verified the emit. Our residual harness warm-starts the MCP at the NLP's own KKT point and evaluates every row (`iterlim=0`):

```
model: rocket    tol: 0.001 (relative)
dual scale: 4.56
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 1.53e-10 raw)
verdict: CASE_C_OBJDEF — objective-defining-intermediate-variable non-convexity
max-residual row: stat_ht(h0)   rel = 1.00e+00  (raw -4.56e+00)
top rows: stat_ht(h0) 1.00 · stat_step 0.497 · stat_ht(h50) 0.438 · stat_v(h0) 0.038 · stat_t(h49) 3.15e-04
```

Two things follow:

1. **The dual transfer closes to 1.53e-10** and complementarity infeasibility is exactly 0 — the multipliers we emit reconcile with the NLP's marginals.
2. **The residual is concentrated entirely on the boundary and terminal rows** — `stat_ht(h0)` (initial altitude), `stat_ht(h50)` (terminal), `stat_step` (time step) — while the *interior* rows are at or near tolerance. Those boundary residuals **move with the warm-start value**, which is the signature we associate with non-convexity at the boundary rather than a defect in the emitted derivatives.

So we believe the MCP is a faithful KKT encoding, and the non-convergence is a property of the problem as PATH sees it. **If that inference is wrong, that is itself a useful answer** — it would redirect us to our own emitter.

---

## 4. What we have already ruled out

Every lever reachable from the emitter or from PATH options. **None converges; all remain MODEL STATUS 5.**

| Lever | Mechanism | Result |
|---|---|---|
| `proximal_perturbation` {1e-2, 1e-1, 1.0, 1e2} | Levenberg–Marquardt Jacobian regularization | MS-5; INFES 477 → 456–482, no monotone gain |
| `crash_method pnewton` + `crash_perturb yes` | projected-Newton crash to a better basis | MS-5; INFES 477, unchanged |
| `merit_function normal` + `gradient_step_limit` | non-monotone merit steering | MS-5; INFES → **382**, best of all configs |
| Combined (`merit normal` + `pp 1e-1` + `crash pnewton`, 20k/500k iters) | | MS-5; INFES 458 |
| **μ-continuation homotopy** | `proximal_perturbation` continuation μ: 1e3 → 0, warm restart each step | **MS-5 at every continuation step** |
| **Multi-start** | `.l`-perturbation re-solve loop | superseded — warm-starting from the NLP optimum *itself* already fails |
| **Division-by-variable reformulation** | remove all `1/m`, `1/ht²` from the initial Jacobian: `gf` → `g·ht² = g₀·h₀²`; free acceleration `a(h)` with `(a+g)·m = T−D` replacing `(T−D−m·g)/m` in `v_eqn` | reformulated **NLP solves to the same optimum**, but its MCP is **MS-5 cold, MS-5 warm-started from the optimum, and MS-5 at every μ-continuation step** |

**The decisive result is the last row.** We initially suspected the division-by-variable terms (`1/m(h)` in the velocity update, `1/ht(h)²` in gravity) were the source of ill-conditioning. A reformulation that removes **all** division-by-variable from the initial Jacobian still fails, in all three modes. **So the non-convergence appears intrinsic to the discretized optimal-control MCP structure rather than to Jacobian conditioning.**

> **Provenance note.** The `INFES` figures in this table were measured under **GAMS 51.3.0 / PATH 5.2.01**, before our corpus was re-pinned to 54.2.1. The *conclusions* — every lever leaves MS-5 — were re-confirmed under 54.2.1, and the model-level figures in §2 and §3 are current. We did not re-run the full option sweep on 54.2.1, so treat the specific INFES values as indicative rather than exact.

---

## 5. The question

**Which PATH option set, regularization schedule, or model reformulation would you expect to force convergence for this class of discretized optimal-control MCP?**

We have a scaffold that emits a μ-continuation driver and a PATH `optfile` alongside the MCP, so a recommended option set or continuation schedule can be plugged in directly.

A secondary question, if the first has no good answer: **is there a principled way to tell, from the outside, whether an MCP of this shape is genuinely non-convergent versus mis-encoded?** Our residual harness (§3) is our current answer and we would welcome a better one.

---

## 6. Reproducing it

```bash
# Generate the warm-started MCP from the GAMSLib source (seq 319)
python -m src.cli data/gamslib/raw/rocket.gms -o rocket_mcp_presolve.gms --nlp-presolve

# Solve: embedded NLP reaches MODEL STATUS 2; the MCP reaches MODEL STATUS 5
gams rocket_mcp_presolve.gms
```

The generated MCP is attached so no build is needed to inspect it. The forcing scaffold is `--force homotopy` / `--force optfile` on the same command.

---

**Project:** https://github.com/jeffreyhorn/nlp2mcp — open source, non-commercial.
**Contact:** Jeff Horn
