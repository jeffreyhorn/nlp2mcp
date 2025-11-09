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

   * Implement **symbolic differentiation** over the AST, generating derivative ASTs via operator-specific rules.
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

**Status:** 📋 READY TO START (Post Sprint 4 completion)  
**Duration:** 10 days (similar to Sprint 4)  
**Based on:** Sprint 4 Retrospective recommendations and remaining PROJECT_PLAN items

---

## Sprint 5 Priorities (from Sprint 4 Retrospective)

### Priority 1: Fix Min/Max Reformulation Bug (1-2 days)

**Issue:** Auxiliary constraint multipliers for dynamically added equality constraints not included in stationarity equations.

**Research:** See `docs/research/minmax_objective_reformulation.md` for comprehensive analysis of the reformulation issue.

**Root Cause:**
- Min/max reformulation creates auxiliary variables and equality constraints
- KKT assembly doesn't include these new equality multipliers in stationarity equations
- Results in "no ref to var in equ.var" GAMS errors

**Solution Approach (Strategy 2 from research doc):**
- For min/max that defines objective variable: use direct constraints instead of auxiliary variables
- Example: `minimize z` where `z = min(x, y)` → `minimize z` with `z ≤ x, z ≤ y`
- Handles simple cases without auxiliary variables
- Avoids infeasible KKT system

**Implementation Steps:**
1. Detect min/max in objective-defining equations
2. Apply Strategy 2 (Direct Constraints) for simple cases:
   - For `minimize z` where `z = min(x,y)`: convert to `z ≤ x` and `z ≤ y` constraints
   - For `maximize z` where `z = max(x,y)`: convert to `z ≥ x` and `z ≥ y` constraints
3. Update KKT assembly to include auxiliary constraint multipliers in stationarity (general fix)
4. Add comprehensive test cases from research doc (Test Cases 1-5)
5. Verify PATH solver convergence

**Test Cases (from research doc):**
- Test Case 1: Simple min in objective (current failure)
- Test Case 2: Direct min objective  
- Test Case 3: Min in constraint (should already work)
- Test Case 4: Nested min/max
- Test Case 5: Max in maximization

**Acceptance Criteria:**
- All 5 test cases from research doc pass
- PATH solver successfully solves reformulated MCPs
- Remove xfail markers from existing min/max tests
- Documentation updated with reformulation approach

**Related Files:**
- `src/kkt/reformulation.py` - Main reformulation logic
- `src/kkt/assemble.py` - KKT stationarity assembly
- `tests/validation/test_path_solver_minmax.py` - Currently xfailed test

---

### Priority 2: Complete PATH Solver Validation (1 day)

**Status:** Test framework exists, GAMS/PATH licensing now available

**Implementation Steps:**
1. Execute existing PATH validation test suite
2. Run tests in `tests/validation/test_path_solver.py`
3. Run tests in `tests/validation/test_path_solver_minmax.py` (after Priority 1 fix)
4. Investigate and resolve any Model Status 5 (Locally Infeasible) failures
5. Document PATH solver options and troubleshooting

**Test Files:**
- `tests/validation/test_path_solver.py` - Main PATH validation (5 golden files)
- `tests/validation/test_path_solver_minmax.py` - Min/max reformulation tests
- `tests/golden/*.gms` - Golden reference files

**Known Issues to Investigate:**
- 2 golden files (bounds_nlp, nonlinear_mix) fail with Model Status 5
- May indicate modeling issues with KKT reformulation for nonlinear problems

**Acceptance Criteria:**
- All golden files solve successfully with PATH (or documented as expected failures)
- Min/max reformulation tests pass
- PATH solver options documented
- Troubleshooting guide updated

---

### Priority 3: Production Hardening (2-3 days)

**Components:**

**3.1 Error Recovery**
- Graceful handling of numerical issues (NaN, Inf)
- Better error messages for common user mistakes
- Validation of input models before processing

**3.2 Large Model Testing**
- Test with models containing 1000+ variables
- Test with models containing 10000+ equations
- Identify and fix performance bottlenecks

**3.3 Memory Optimization**
- Profile memory usage on large models
- Optimize sparse matrix representations
- Reduce memory footprint where possible

**3.4 Edge Cases**
- Test with empty sets
- Test with unbounded variables
- Test with degenerate constraints
- Test with circular dependencies

**Deliverables:**
- Performance benchmarks updated
- Memory profiling results documented
- Edge case test suite (20+ additional tests)
- Optimization improvements applied

---

### Priority 4: PyPI Packaging (1-2 days)

**Components:**

**4.1 Package Configuration**
- Update `pyproject.toml` with PyPI metadata
- Configure build system (setuptools/hatch)
- Add package classifiers and keywords
- Include README.md and LICENSE in package

**4.2 Wheel Building**
- Test wheel building: `python -m build`
- Test installation from wheel: `pip install dist/*.whl`
- Verify CLI entry point works
- Test on clean virtual environment

**4.3 Release Automation**
- GitHub Actions workflow for PyPI publishing
- Automated version bumping
- Changelog generation
- Release notes template

**4.4 Installation Testing**
- Test `pip install nlp2mcp` (from TestPyPI first)
- Test on multiple Python versions (3.10, 3.11, 3.12)
- Test on multiple platforms (Linux, macOS, Windows)
- Verify dependencies install correctly

**Deliverables:**
- Package published to TestPyPI
- Release automation workflow
- Installation guide in README.md
- Version 0.4.0 released

---

### Priority 5: Documentation Polish (2 days)

**Components:**

**5.1 Tutorial for Beginners**
- Step-by-step guide from installation to first MCP
- Explained examples with visualization
- Common pitfalls and how to avoid them
- Integration with existing USER_GUIDE.md

**5.2 FAQ Section**
- Common questions from user testing
- Performance optimization tips
- Troubleshooting common errors
- Comparison with other tools

**5.3 Troubleshooting Guide**
- Error message reference
- Diagnostic procedures
- When to contact support
- Known limitations and workarounds

**5.4 API Reference**
- Comprehensive docstring coverage
- Auto-generated API docs (Sphinx)
- Usage examples for each public function
- Type hints documentation

**Deliverables:**
- TUTORIAL.md (new file)
- FAQ.md (new file)
- TROUBLESHOOTING.md (enhanced)
- API documentation site (sphinx-based)

---

## Original Sprint 5 Plan (Updated with Priorities Above)

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

