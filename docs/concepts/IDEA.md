How can KKT conditions be used to transform a Nonlinear Program (NLP) into a Mixed Complementarity Problem (MCP).

Great question. The standard recipe is:

* start with your nonlinear program (NLP),
* write down its KKT conditions,
* and then encode those KKT conditions as a **Mixed Complementarity Problem (MCP)**: equations for stationarity/equalities, plus complementarity pairs for inequalities and bounds.

Below is a compact, “drop-in” blueprint you can reuse.

---

# 1) Start from a generic NLP

Minimize (f(x))
subject to
[
\begin{aligned}
g_i(x) &\le 0 \quad (i=1,\dots,m),\
h_j(x) &= 0 \quad (j=1,\dots,p),\
\ell ;\le; x ;\le; u \quad &(\text{componentwise bounds; any of }\ell_k,u_k \text{ may be } \pm\infty).
\end{aligned}
]

# 2) KKT conditions

Introduce Lagrange multipliers:

* (\lambda \in \mathbb{R}^m_{\ge 0}) for the inequalities (g(x)\le 0),
* (\nu \in \mathbb{R}^p) (free) for equalities (h(x)=0),
* (\pi^L,\pi^U \in \mathbb{R}^n_{\ge 0}) for the lower/upper bounds on (x).

KKT system:

1. **Stationarity**
   [
   \nabla f(x) + J_g(x)^\top \lambda + J_h(x)^\top \nu - \pi^L + \pi^U ;=; 0.
   ]

2. **Primal feasibility**
   [
   g(x)\le 0,\quad h(x)=0,\quad \ell \le x \le u.
   ]

3. **Dual feasibility**
   [
   \lambda \ge 0,\quad \pi^L \ge 0,\quad \pi^U \ge 0.
   ]

4. **Complementarity**
   [
   \lambda_i ,\perp, g_i(x);;(\forall i),\qquad
   \pi^L_k ,\perp, x_k-\ell_k;;(\forall k),\qquad
   \pi^U_k ,\perp, u_k-x_k;;(\forall k).
   ]

Here (a \perp b) means (a\ge 0,; b\ge 0,; a^\top b=0).

> Notes:
> • These are *necessary* under a standard constraint qualification (e.g., LICQ/MFCQ).
> • If (f) is convex, (g) convex, and (h) affine, they’re also *sufficient* for global optimality.

# 3) Encode as an MCP

An MCP is: find (z) such that for each component (i),
[
a_i \le z_i \le b_i \quad\text{and}\quad
\begin{cases}
z_i\in(a_i,b_i) \Rightarrow F_i(z)=0,\
z_i=a_i \Rightarrow F_i(z)\ge 0,\
z_i=b_i \Rightarrow F_i(z)\le 0,
\end{cases}
]
often written compactly as (a \le z \le b ;\perp; F(z)).

Define variables and functions:

* Variables (z := (x,\lambda,\nu,\pi^L,\pi^U)).
* Mapping (F(z)) with blocks
  [
  \begin{aligned}
  F_x &:= \nabla f(x) + J_g(x)^\top \lambda + J_h(x)^\top \nu - \pi^L + \pi^U,\
  F_\lambda &:= -,g(x),\
  F_\nu &:= h(x),\
  F_{\pi^L} &:= x-\ell,\
  F_{\pi^U} &:= u-x.
  \end{aligned}
  ]

Bounds to produce the right complementarity behavior:

* (x) is **free** (no MCP bounds): ((a,b)=(-\infty,+\infty)) and enforce (F_x=0) (stationarity).
* (\lambda \ge 0) with (F_\lambda = -g(x)): this enforces (0\le \lambda \perp -g(x)\ge 0), i.e., (\lambda \perp g(x)\le 0).
* (\nu) is **free** with (F_\nu=h(x)=0) (equalities stay as equations).
* (\pi^L \ge 0) with (F_{\pi^L}=x-\ell): (0\le \pi^L \perp x-\ell \ge 0).
* (\pi^U \ge 0) with (F_{\pi^U}=u-x): (0\le \pi^U \perp u-x \ge 0).

That’s exactly your KKT system as an MCP.

> Implementation tip: many MCP solvers (PATH, KNITRO-MPEC, IPOPT-MPEC, etc.) accept **mixed** rows: some variables are free with equations (stationarity & equalities), while others are in complementarity pairs (inequalities/bounds). Sign conventions vary; the (-g(x)) choice above is the common “(0\le \lambda \perp -g(x)\ge 0)” form.

# 4) Minimal worked example

NLP:
[
\min_x ;\tfrac12(x-3)^2 \quad \text{s.t.}; x\ge 0.
]
Rewrite constraint as (g(x)=-x\le 0). Variables: (x) (free), (\lambda\ge 0) for (g), (\pi^L=0) and (\pi^U=0) since we won’t use bound multipliers here (we folded the bound into (g)).

* Stationarity: (F_x = (x-3) + \lambda(-1) = 0 ;\Rightarrow; x-3-\lambda=0).
* Complementarity: (0\le \lambda \perp -g(x)=x \ge 0).

MCP:

* (x) free with (F_x=0).
* (\lambda \ge 0) with (F_\lambda=-g(x)=x).

Solutions satisfy (x\ge 0), (\lambda\ge 0), (x\lambda=0), and (x-3-\lambda=0). The solution is (x=3,\lambda=0).

# 5) Practical solver patterns

* **GAMS/PATH (MCP):** put the five blocks (F_x,F_\lambda,F_\nu,F_{\pi^L},F_{\pi^U}) as equations; bind each to variables with the bounds above.
* **Pyomo (mpec):** use `Complementarity` components:

  * `complements(inequality_body <= 0, multipliers >= 0)` for (g,\lambda),
  * equality rows as `Constraint` (or MCP row with free var),
  * stationarity as a `Constraint`.
* **Bound handling:** either introduce (\pi^L,\pi^U) (as shown) or, if your modeling system supports **box MCP**, directly declare (x \in [\ell,u]) and set (F_x) as the row paired with (x). Both are equivalent.
* **Nonconvex caution:** The MCP encodes KKT **stationary points**. In nonconvex problems, solving the MCP can return local optima or saddles. Warm starts and merit filters help.
* **Constraint qualification:** If LICQ/MFCQ fails, KKT may not hold; the MCP may be singular or have spurious solutions. Consider regularization (e.g., penalize (h(x))), or use stronger stationarity notions (M-/S-stationarity for MPECs).
* **Alternative (NCP function):** If you only have inequalities and want to keep it as an NLP, replace each complementarity (0\le a \perp b \ge 0) by an **NCP function** such as Fischer–Burmeister (\phi(a,b)=0). Many NLP solvers handle this well, but it’s no longer an MCP.

# 6) Quick checklist (copy/paste)

1. Write (f,g,h,\ell,u).
2. Build stationarity (F_x=\nabla f + J_g^\top\lambda + J_h^\top\nu - \pi^L + \pi^U).
3. Set (F_\lambda=-g(x)), (F_\nu=h(x)), (F_{\pi^L}=x-\ell), (F_{\pi^U}=u-x).
4. Variable bounds:

   * (x,\nu) free (equations (F_x=0,F_\nu=0));
   * (\lambda,\pi^L,\pi^U \ge 0) and **complementary** to (F_\lambda,F_{\pi^L},F_{\pi^U}).
5. Send ((F,z,\text{bounds})) to your MCP solver.
