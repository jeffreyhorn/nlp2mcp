Here’s a concrete five-sprint (2 weeks each) plan to build **nlp2mcp**, a Python tool that converts a GAMS NLP into an equivalent GAMS MCP by generating the KKT system.

---

# Sprint 1 (Weeks 1–2): MVP parser + model IR

**Goal:** Parse a practical subset of GAMS NLP into a clean **intermediate representation (IR)** with everything normalized for later differentiation and codegen.

### Scope & assumptions (v1 subset)

* One `Solve ... using NLP [min/max]` block.
* `Sets`, `Aliases`, `Parameters`, `Scalars`, `Variables`, `Equations`.
* Indexed variables/parameters over finite sets; `sum()` aggregations.
* Equation relations: `=e=`, `=l=`, `=g=`.
* Bounds via `x.lo(i)` / `x.up(i)`, and constants (±INF supported).
* Expression ops: `+ - * / pow`, `exp log sqrt`, `sin cos tan`, `abs` (flag for v2 or handled via smoothing later).
* No loops/flow control (`loop`, `$if/$elseif/$include`) in v1. (Detected and rejected gracefully.)

### Components

1. **Grammar & lexer**

   * Use `lark` with a dedicated GAMS-subset grammar file.
   * Tokens: identifiers (with optional quotes), numbers, strings, keywords (`Sets`, `Variables`, `Equations`…), indexing `(i,j)`, `sum(i, expr)`.
2. **Symbol table**

   * Track **sets** (universe, members), **aliases**, **parameters** (with dimensions), **variables** (domains, bounds), **equations** (domain, relation).
   * Resolve cross-references; expand aliases.
3. **Expression AST**

   * Node types: `Const`, `VarRef(name, index_tuple)`, `ParamRef(...)`, `Unary(op, child)`, `Binary(op, left, right)`, `Sum(index_set, body)`, `Call(func, args)`.
   * Attach shape/arity and domain info (e.g., an equation over set `i`).
4. **Normalization pass**

   * Convert `=l=`/`=g=` to `<= 0` form: store as `g(x) <= 0` (i.e., move RHS to left).
   * Expand implicit RHS constants to AST constants.
   * Collect **primal bounds** from `x.lo/.up` into the IR; normalize `±INF`.
   * Canonicalize equations to: `lhs - rhs` with a relation tag.
5. **IR design**

   * `ModelIR`: sets, symbols, variables (with bounds), equations list (each with domain set, relation, AST).
   * `ObjectiveIR`: sense (`min`/`max`), AST; objective variable name if present.
6. **Validation & helpful errors**

   * Undefined symbols, dimension mismatches, illegal operations, unsupported features.
   * Crisp error messages with line/column spans.

### Deliverables

* `gams_grammar.lark`
* `parser.py`, `symbols.py`, `ast.py`, `ir.py`, `normalize.py`
* Unit tests: ~40 parsing/IR tests; 10 normalization tests.
* Example inputs: 5 tiny NLPs (scalar and indexed).

### Acceptance criteria

* Given subset GAMS files, produce a deterministic `ModelIR`.
* Inequalities and bounds normalized and retrievable from IR.
* Clear errors for unsupported constructs.

---

# Sprint 2 (Weeks 3–4): Differentiation engine (AD) + Jacobians

**Goal:** Build gradients/Jacobians on the IR to support KKT stationarity and constraint Jacobians using a purely symbolic differentiation pipeline.

### Components

1. **AD core**

   * Implement **symbolic** AD over the AST, generating derivative ASTs via operator-specific rules (replaces the earlier reverse-mode assumption).
   * Support all v1 functions (add, mul, div, pow, exp, log, trig). Provide derivative rules and numeric guards (e.g., `log(x)` domain).
2. **Index & aggregation handling**

   * `sum(i, body)`: AD should treat as linear aggregation over the inner derivatives of `body`.
   * Produce sparse Jacobian structures keyed by `(row, var_instance)`.
3. **Shaping & sparsity**

   * Each equation (possibly indexed over sets) yields multiple rows; each variable (possibly indexed) yields multiple columns.
   * Generate a **sparse map**: `J[eq_row][var_col] := AST(expr)` (still symbolic ASTs—stringifiable).
4. **Objective gradient**

   * Compute `∇f(x)` as a vector over all variable instances.
   * Handle objective **max** by flipping sign (convert to `min` internally).
5. **Safety & reproducibility**

   * Automatic checks for NaNs/Infs at AD time for numeric examples.
   * Deterministic ordering (sorted set iteration).
6. **Testing**

   * Analytical vs. finite-difference checks on random instances (small sets).
   * Corner cases: constants eliminated; zero derivatives; chained functions.

### Deliverables

* `ad.py` (symbolic differentiation engine)
* `jacobian.py` (equation/variable indexing, sparsity extraction)
* Tests: ~30 derivative rule tests; ~20 Jacobian sparsity tests; ~10 numeric FD validations.

### Acceptance criteria

* For each test NLP, produce correct `∇f`, `J_g`, `J_h` shapes and values (±1e-6 FD agreement).
* Supports indexed sums and multi-dimensional variables/equations.

---

# Sprint 3 (Weeks 5–6): KKT synthesis + GAMS MCP codegen

**Goal:** Map IR + derivatives to a **KKT system** and emit runnable **GAMS MCP**.

### Components

1. **KKT assembler**

   * Partition constraints: `equalities` (h), `inequalities` (g≤0).
   * Create multiplier symbol sets: `lam(m)` for each inequality row, `nu(p)` for each equality row.
   * For primal bounds: synthesize `piL(i)`, `piU(i)` for every primal variable instance with finite lo/up.
   * Build stationarity:
     [
     F_x = ∇f + J_g^\top λ + J_h^\top ν - π^L + π^U
     ]
   * Build complementarity sides:

     * `Flam = -g(x)`, `Fnu = h(x)`, `FpiL = x - lo`, `FpiU = up - x`.
2. **GAMS emitter (templates)**

   * Emit `Sets` for indexing rows of `lam`, `nu`, and the variable index sets.
   * Emit `Variables` and `Positive Variables` blocks.
   * Emit `Equations` blocks with one equation per row (expand indices to concrete equations).
   * Equations syntax:

     * Stationarity rows `=E=` 0.
     * Complementarity rows emitted with `=G=` 0 **and** paired with positive variables in the `Model` declaration (`/ Fx.x, Flam.lam, ... /`).
   * Respect **sign conventions** (`-g(x) =G= 0` etc.)
3. **Box-vs-explicit bounds**

   * If original model had explicit bound constraints (e.g., `x(i) >= 0` as equations), **do not** duplicate. Prefer using `lo/up` whenever possible; warn if both appear.
4. **Scalar & indexed examples**

   * Generate clean, human-readable names with prefixes (`lam_c2(i)`) avoiding collisions.
   * INF bounds → skip the corresponding `piL/piU` and equations.
5. **End-to-end smoke runner**

   * Optional: if PATH is present, run GAMS to verify the generated MCP solves on the example models (enable/skip flag).
   * Otherwise, validate that GAMS compiles (syntax check mode) by producing a `.gms` and (optionally) running in a dockerized GAMS if available.

### Deliverables

* `kkt.py` (assembler)
* `emit_gams.py` (codegen templates)
* `cli.py` with `nlp2mcp input.gms -o out_mcp.gms`
* 5 end-to-end golden tests (input `.gms` → output `.gms` string compare) + optional integration if GAMS available.

### Acceptance criteria

* For all v1 examples, emitted MCP compiles in GAMS and passes text-golden diffs.
* Stationarity and complementarity equations match the KKT construction formally.

---

# Sprint 4 (Weeks 7–8): Feature expansion + robustness

**Goal:** Broaden language coverage, improve numerics, and add quality-of-life features.

### Language & modeling features

* **Includes & parameters:**

  * Support `$include` for simple parameter files (string-substitute, no conditionals).
  * Load data blocks for parameters/sets (`Table`, `Parameter` assignments).
* **More functions:**

  * Add `min/max` with either (a) rejection, (b) smoothing (e.g., `softmax`/`softplus`) flag, or (c) auxiliary/epigraph reformulation flag (document limits).
  * `abs(x)`: provide `--smooth-abs` (Huber/softabs) vs. `--reject-nondiff`.
* **Bounds ingestion:**

  * Recognize `x.fx = c;` (fixed) → encode as equality in MCP (both `lo` and `up` equal → no `piL/piU`, but `x=c` equality).
* **Scaling & numerics:**

  * Row/column scaling heuristics (e.g., scale equations so Jacobian row norm ≈ 1).
  * Option `--scale none|auto|byvar`.
* **Diagnostics:**

  * Print model stats (rows/cols/nonzeros, # of g/h, # of piL/piU).
  * Optional dump of Jacobian pattern in Matrix Market for debugging.

### Developer ergonomics

* **Error messages** enriched with source ranges & suggestions.
* **Configuration**: `pyproject.toml` options and CLI flags.
* **Logging**: structured logs; verbosity levels.

### Deliverables

* Extended parser (support `$include`, parameter blocks).
* `smoothing.py` (opt-in smoothers), `scaling.py`.
* CLI flags: `--smooth-abs`, `--reject-nondiff` (default), `--scale`, `--emit-comments`.
* More examples: 10 mid-size models (transport-style indexed constraints, nonlinear costs).

### Acceptance criteria

* New examples parse and convert; where smoothing is requested, emitted MCP reflects chosen policy and compiles.
* Scaling transforms don’t change KKT semantics (only multiply rows/columns with documentation).

---

# Sprint 5 (Weeks 9–10): Hardening, packaging, docs, and ecosystem hooks

**Goal:** Ship a reliable tool with docs, CI, and optional exporters.

### Packaging & distribution

* Package as `nlp2mcp` on PyPI.
* `pip install nlp2mcp` installs CLI and library.
* Semantic versioning; changelog.

### CI/CD & QA

* GitHub Actions:

  * Lint (`ruff`, `black`), type check (`mypy`).
  * Unit + golden tests.
  * Optional matrix that runs GAMS syntax check in a container if license present (skippable).
* **Corpus regression tests**:

  * Keep a “model zoo” folder; golden outputs tracked.
  * Fuzz tests: random coefficient scalings, index permutations, FD sanity checks.

### Documentation

* **User guide** (mkdocs):

  * Install, quick start (`nlp2mcp model.gms`).
  * Supported GAMS subset & feature matrix.
  * How KKT→MCP works (with equations).
  * Troubleshooting (nondifferentiable, missing data, INF bounds).
* **Developer guide**:

  * IR reference, AD design, codegen templates.
  * How to add new functions/operators.
* **Examples**:

  * 12 curated examples (scalar, indexed, convex, nonconvex) with expected MCP snippets.

### Ecosystem hooks (optional but valuable)

* **Exporter: Pyomo-MPEC**

  * Alternate backend to emit Pyomo `Complementarity` objects.
  * CLI: `--backend gams-mcp|pyomo-mpec` (default gams-mcp).
* **EMP annotations helper**

  * (Docs only) Show how to achieve similar results with GAMS EMP; include comparison.

### Deliverables

* Publishable package, docs site, release notes.
* Optional Pyomo backend (`emit_pyomo.py`) + examples.

### Acceptance criteria

* Clean install from PyPI, CLI works.
* Docs site covers install → convert → run.
* CI green; model zoo conversions stable over commits.

---

## Architecture & file layout (suggested)

```
nlp2mcp/
  __init__.py
  cli.py
  gams/
    grammar.g4 or gams_grammar.lark
    parser.py
    tokens.py
  ir/
    symbols.py
    ast.py
    model_ir.py
    normalize.py
  ad/
    ad_core.py
    jacobian.py
  kkt/
    assemble.py
  emit/
    emit_gams.py
    emit_pyomo.py
  utils/
    errors.py
    logging.py
    scaling.py
    smoothing.py
tests/
  unit/
  golden/
  e2e/
examples/
docs/
pyproject.toml
```

---

## Risks & mitigations

* **GAMS feature breadth** → start with a **documented subset** (Sprint 1), reject clearly; expand in Sprint 4.
* **Nondifferentiable ops** → default reject; provide smoothing flags (Sprint 4).
* **Index shenanigans** (aliases, multi-dimensional sums) → robust symbol table & index validation (Sprint 1–2).
* **Numeric fragility** (nonconvex KKT) → emphasize that MCP encodes stationarity; add scaling and warm-start tips in docs (Sprint 4–5).

---

## Definition of Done (overall)

* Converts the documented subset of GAMS NLPs into correct, compilable GAMS MCPs implementing KKT.
* Derivatives verified by FD on test corpus.
* Clear CLI UX, docs, and examples; reproducible builds/tests.

If you want, I can also draft the initial `gams_grammar.lark` and the IR class stubs so Sprint 1 can start with copy-pasteable code.
