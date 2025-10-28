Could a (python) program be written that would take Nonlinear program expressed in GAMS code as input and output GAMS code for an equivalent MCP?

Short answer: yes—totally feasible. You can write a Python tool that takes a GAMS NLP, extracts the objective/constraints/bounds, forms the KKT system, and emits a GAMS **MCP** model. Below is a practical blueprint you can implement (and a tiny end-to-end example).

---

# What your converter must do

## 1) Parse the NLP

Goal: recover

* decision vars (x) with bounds (\ell \le x \le u)
* objective (f(x)) (+ sense: min/max)
* equalities (h(x)=0)
* inequalities (g(x)\le 0) (normalize signs)

Implementation options:

* **Parse GAMS text** into an AST (e.g., with `lark` or ANTLR4; you’ll define a “NLP subset of GAMS” grammar: sets/params/vars/equations/objective/solve).
* Or require **light annotations** in comments (e.g., `!objective: obj`, `!equalities: con1,con2`, `!inequalities: cap,bal`) to avoid deep static analysis of the solve statement.
* Resolve any `=g=`, `=l=`, `=e=` into `<= / >= / =` and normalize to `<= 0` for inequalities.

## 2) Differentiate

You need (\nabla f(x)), (J_g(x)), (J_h(x)).

* Build elementary expression nodes (+, −, *, /, pow, exp, log, sin, cos, …) and implement **forward or reverse-mode AD** on your AST.
* Support GAMS functions you care about; for unknown/external functions, either (a) reject, (b) require user-supplied derivatives, or (c) fallback to finite-diff (works but less robust).

## 3) Synthesize KKT → MCP blocks

Introduce multipliers:

* (\lambda \ge 0) for each (g_i(x)\le 0)
* (\nu) (free) for each (h_j(x)=0)
* (\pi^L,\pi^U \ge 0) for bounds (\ell \le x \le u)

Build functions:
[
\begin{aligned}
F_x(x,\lambda,\nu,\pi^L,\pi^U) &= \nabla f(x)+J_g(x)^\top\lambda+J_h(x)^\top\nu-\pi^L+\pi^U,\
F_\lambda &= -g(x),\quad
F_\nu = h(x),\quad
F_{\pi^L} = x-\ell,\quad
F_{\pi^U}=u-x.
\end{aligned}
]

Pairings (MCP sense):

* (x,\nu) are **free** with equations (F_x=0, F_\nu=0).
* (0\le \lambda \perp F_\lambda \ge 0)  (i.e., (\lambda \perp g(x)\le 0)).
* (0\le \pi^L \perp F_{\pi^L}\ge 0), (0\le \pi^U \perp F_{\pi^U}\ge 0).

## 4) Emit GAMS MCP code

Generate:

* `Variables` for (x,\lambda,\nu,\pi^L,\pi^U)
* `Equations` for each component of (F_x,F_\lambda,F_\nu,F_{\pi^L},F_{\pi^U})
* A `Model` using MCP and a `Solve` with PATH (or other MCP solver).

---

# Skeleton of emitted GAMS (template)

```gams
* --- generated from NLP → KKT(MCP) ---

Sets
    i  / i1*iN /         * variables x(i)
    m  / m1*mM /         * inequalities g_m(x) <= 0
    p  / p1*pP / ;       * equalities   h_p(x)  = 0

Parameters
    ell(i), uu(i);       * bounds on x (use ±INF where absent)

Variables
    x(i)                 * primal
    lam(m)               * λ >= 0
    nu(p)                * ν free
    piL(i)               * π^L >= 0
    piU(i)               * π^U >= 0
    ;

Positive Variables lam, piL, piU;
x.lo(i) = ell(i);
x.up(i) = uu(i);

Equations
    Fx(i)                * stationarity components
    Flam(m)              * -g_m(x)
    Fnu(p)               *  h_p(x)
    FpiL(i)              * x(i) - ell(i)
    FpiU(i)              * uu(i) - x(i)
    ;

* --- auto-differentiated expressions plugged here:
Fx(i)   ..  <grad_f(i)>
          + sum(m, <Jg(m,i)> * lam(m))
          + sum(p, <Jh(p,i)> * nu(p))
          - piL(i) + piU(i) =E= 0;

Flam(m) ..  - (<g(m)>)  =G= 0;   * 0 <= lam ⟂ -g(x) >= 0
Fnu(p)  ..   <h(p)>     =E= 0;
FpiL(i) ..   x(i) - ell(i) =G= 0; * 0 <= piL ⟂ x-ell >= 0
FpiU(i) ..   uu(i) - x(i) =G= 0;  * 0 <= piU ⟂ uu-x >= 0

Model kkt_mcp / Fx.x, Flam.lam, Fnu.nu, FpiL.piL, FpiU.piU /;
Solve kkt_mcp using MCP;
```

Your generator fills in `<grad_f(i)>`, `<Jg(m,i)>`, `<Jh(p,i)>`, `<g(m)>`, `<h(p)>` using the AD results.

---

# End-to-end toy example

### Input GAMS (NLP)

```gams
Sets i / x1*x2 /;
Variables x(i), z;
Equations obj, c1, c2;

x.lo('x1') = 0; x.up('x1') = 10;
x.lo('x2') = -inf; x.up('x2') = +inf;

obj.. z =E= 0.5*sqr(x('x1')-3) + exp(x('x2'));
c1..  x('x1') + x('x2') =E= 2;
c2..  2*x('x1') - x('x2') =L= 5;

Model nlp /obj, c1, c2/;
Solve nlp using NLP minimizing z;
```

### Emitted GAMS (MCP, abridged)

```gams
Sets i / x1*x2 /, m / c2 /, p / c1 /;

Variables x(i), lam(m), nu(p), piL(i), piU(i);

Positive Variables lam, piL, piU;

x.lo('x1') = 0; x.up('x1') = 10;

Equations Fx(i), Flam(m), Fnu(p), FpiL(i), FpiU(i);

* grads/Jacobians inserted by the generator:
Fx('x1').. (x('x1')-3) + ( 0 ) + ( 1 )*nu('c1') - piL('x1') + piU('x1') =E= 0;
Fx('x2').. exp(x('x2')) + ( 0 ) + ( 1 )*nu('c1') - piL('x2') + piU('x2') =E= 0;

Flam('c2').. -( 2*x('x1') - x('x2') - 5 ) =G= 0;
Fnu('c1') ..   ( x('x1') + x('x2') - 2 )  =E= 0;

FpiL(i) .. x(i) - x.lo(i) =G= 0;
FpiU(i) .. x.up(i) - x(i) =G= 0;

Model kkt_mcp / Fx.x, Flam.lam, Fnu.nu, FpiL.piL, FpiU.piU /;
Solve kkt_mcp using MCP;
```

(Here the inequality `c2: 2*x1 - x2 <= 5` was normalized to `g = 2*x1 - x2 - 5 <= 0`.)

---

# Engineering notes & pitfalls

* **Parsing scope:** GAMS is a big language. Start with a *subset*: scalar/param/set declarations; algebraic expressions; `=e=`, `=l=`, `=g=` equations; `x.lo/x.up`; single objective; one `Solve`. Ignore loops, `$ifthen`, macros, etc., at first.
* **Sign conventions:** Convert all inequalities to `g(x) <= 0`. For `>=`, multiply by −1.
* **Bounds vs separate constraints:** Prefer to keep box bounds as `x.lo/x.up` (cleaner MCP via (\pi^L,\pi^U)). If the original model used explicit constraints for bounds, you can either keep them as (g)’s or fold them into lo/up when safe.
* **Non-differentiability:** Flag `abs`, `max`, `min`, piecewise constructs. Either (a) reject, (b) smooth, or (c) introduce auxiliaries to keep differentiability.
* **External/user functions:** Require derivative hooks; otherwise reject.
* **Scaling:** Consider auto-scaling residuals or user options; MCP solvers appreciate it.
* **Optimality vs stationarity:** For nonconvex NLPs the KKT MCP finds stationary points (could be saddle). That’s intrinsic to the transformation.

---

# Reality check: do you even need Python?

GAMS has **EMP (Extended Mathematical Programming)** features that can automatically create KKT/MCP reformulations of NLPs with light annotations. If your goal is *“inside GAMS, produce KKT/MCP”*, EMP might already cover your use-case without writing a converter. If you want a **standalone** tool (e.g., for auditing, exporting, or customizing), then the Python route above is the right path.

---

# Minimal Python project plan

* Parser: `lark` with a compact grammar for your subset; build expression AST.
* AD: simple reverse-mode on your node types; emit GAMS strings for primal/Jacobian entries.
* Normalizer: turn each eqn into either equality or normalized `<= 0` inequality; collect bounds.
* Generator: fill the GAMS MCP template (variables, equations, model/solve).
* CLI: `nlp2kkt input.gms -o output_kkt.gms --sense=min`.

If you want, share a sample `.gms` and I’ll sketch the exact emitted MCP for that case (we can keep to your favorite operators so the first pass “just works”).

