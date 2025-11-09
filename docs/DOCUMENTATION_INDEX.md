# nlp2mcp Documentation Index

**Complete guide to all documentation resources**

Version: 0.5.0-beta  
Last Updated: 2025-11-08

---

## Quick Start

New to nlp2mcp? Start here:

1. **[README](../README.md)** - Project overview and quick start
2. **[TUTORIAL](TUTORIAL.md)** - Step-by-step learning guide (1-2 hours)
3. **[USER_GUIDE](USER_GUIDE.md)** - Complete feature reference

---

## User Documentation

### Getting Started

- **[README.md](../README.md)** - Project overview, installation, quick examples
- **[TUTORIAL.md](TUTORIAL.md)** - Comprehensive tutorial with runnable examples
  - Introduction and prerequisites
  - First conversion walkthrough
  - Understanding KKT output
  - Common patterns and advanced features
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete reference manual
  - All command-line options
  - Sprint 4 features (min/max, abs(), fixed variables, scaling)
  - Configuration and examples
  - Advanced topics

### Problem Solving

- **[FAQ.md](FAQ.md)** - 35 frequently asked questions
  - Installation & setup
  - Basic usage
  - Conversion process
  - Advanced features
  - PATH solver
  - Troubleshooting
  - Performance & limitations
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem → Diagnosis → Solution
  - Installation issues
  - Parsing errors
  - Model validation errors
  - Conversion failures
  - Numerical errors
  - PATH solver issues
  - Performance problems
  - Output issues

### Solver Integration

- **[PATH_SOLVER.md](PATH_SOLVER.md)** - Complete PATH solver guide
  - PATH options reference
  - Configuration templates (standard/difficult/failing cases)
  - Troubleshooting decision tree
  - Interpreting PATH output
  - Model status codes
- **[PATH_REQUIREMENTS.md](PATH_REQUIREMENTS.md)** - PATH installation and licensing

### Project Information

- **[LIMITATIONS.md](LIMITATIONS.md)** - Known limitations and workarounds
- **[VERSIONING.md](release/VERSIONING.md)** - Semantic versioning strategy
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes

---

## Developer Documentation

### Architecture

- **[SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md)** - High-level system design
- **[DATA_STRUCTURES.md](architecture/DATA_STRUCTURES.md)** - Core data structures
- **[NLP2MCP_HIGH_LEVEL.md](concepts/NLP2MCP_HIGH_LEVEL.md)** - Conceptual overview

### Module Documentation

#### Parser & IR
- **[parser_output_reference.md](ir/parser_output_reference.md)** - Parser output format

#### Automatic Differentiation
- **[ad/DESIGN.md](ad/DESIGN.md)** - AD system design
- **[ad/ARCHITECTURE.md](ad/ARCHITECTURE.md)** - AD architecture
- **[ad/DERIVATIVE_RULES.md](ad/DERIVATIVE_RULES.md)** - Differentiation rules
- **[ad/README.md](ad/README.md)** - AD module overview

#### KKT Assembly
- **[kkt/KKT_ASSEMBLY.md](kkt/KKT_ASSEMBLY.md)** - KKT system assembly process

#### Code Generation
- **[emit/GAMS_EMISSION.md](emit/GAMS_EMISSION.md)** - GAMS code generation

### API Reference

- **[API Documentation](api/index.html)** - Auto-generated API docs (Sphinx)
  - Complete module, class, and function reference
  - Type hints and docstrings
  - Source code links

---

## Sprint Documentation

### Sprint 5 (Current - Hardening & Release)

- **[PLAN.md](planning/SPRINT_5/PLAN.md)** - Sprint 5 detailed plan
- **[KNOWN_UNKNOWNS.md](planning/SPRINT_5/KNOWN_UNKNOWNS.md)** - Research findings
- **[CHECKPOINT_1_REPORT.md](planning/SPRINT_5/CHECKPOINT_1_REPORT.md)** - Min/max fix checkpoint
- **[CHECKPOINT_2_REPORT.md](planning/SPRINT_5/CHECKPOINT_2_REPORT.md)** - Hardening checkpoint
- **[CHECKPOINT_3.md](planning/SPRINT_5/CHECKPOINT_3.md)** - Release readiness checkpoint

### Sprint 4 (Advanced Features)

- **[PLAN.md](planning/SPRINT_4/PLAN.md)** - Sprint 4 plan
- **[RETROSPECTIVE.md](planning/SPRINT_4/RETROSPECTIVE.md)** - Sprint 4 retrospective
- **[KNOWN_UNKNOWNS.md](planning/SPRINT_4/KNOWN_UNKNOWNS.md)** - Sprint 4 research

### Sprint 3 (Testing & Validation)

- **[PLAN.md](planning/SPRINT_3/PLAN.md)** - Sprint 3 plan
- **[RETROSPECTIVE.md](planning/SPRINT_3/RETROSPECTIVE.md)** - Sprint 3 retrospective
- **[SUMMARY.md](planning/SPRINT_3/SUMMARY.md)** - Sprint 3 summary

### Sprint 2 (Jacobian & Differentiation)

- **[PLAN.md](planning/SPRINT_2/PLAN.md)** - Sprint 2 plan
- **[RETROSPECTIVE.md](planning/SPRINT_2/RETROSPECTIVE.md)** - Sprint 2 retrospective
- **[SUMMARY.md](planning/SPRINT_2/SUMMARY.md)** - Sprint 2 summary

### Sprint 1 (Foundation)

- **[SUMMARY.md](planning/SPRINT_1/SUMMARY.md)** - Sprint 1 summary

---

## Research & Design Documents

### Research

- **[minmax_objective_reformulation.md](research/minmax_objective_reformulation.md)** - Min/max reformulation research
- **[minmax_path_validation_findings.md](research/minmax_path_validation_findings.md)** - PATH validation
- **[convexity_detection.md](research/convexity_detection.md)** - Convexity analysis
- **[RESEARCH_SUMMARY_FIXED_VARIABLES.md](research/RESEARCH_SUMMARY_FIXED_VARIABLES.md)** - Fixed variables
- **[RESEARCH_SUMMARY_TABLE_SYNTAX.md](research/RESEARCH_SUMMARY_TABLE_SYNTAX.md)** - Table syntax

### Design Documents

- **[minmax_kkt_fix_design.md](design/minmax_kkt_fix_design.md)** - Min/max KKT fix design

---

## Testing & Validation

### Testing Strategy

- **[TEST_PYRAMID.md](testing/TEST_PYRAMID.md)** - Testing strategy and pyramid
- **[EDGE_CASE_MATRIX.md](testing/EDGE_CASE_MATRIX.md)** - Edge case coverage
- **[ERROR_MESSAGE_VALIDATION.md](testing/ERROR_MESSAGE_VALIDATION.md)** - Error message quality

### Validation Reports

- **[PATH_VALIDATION_RESULTS.md](validation/PATH_VALIDATION_RESULTS.md)** - PATH solver validation
- **[PATH_SOLVER_STATUS.md](testing/PATH_SOLVER_STATUS.md)** - PATH solver status
- **[DAY5_PERFORMANCE_REPORT.md](performance/DAY5_PERFORMANCE_REPORT.md)** - Performance benchmarks

---

## Release & Packaging

- **[VERSIONING.md](release/VERSIONING.md)** - Version numbering strategy
- **[PYPI_PACKAGING_PLAN.md](release/PYPI_PACKAGING_PLAN.md)** - PyPI packaging plan
- **[TESTPYPI_PUBLISH.md](release/TESTPYPI_PUBLISH.md)** - TestPyPI publishing guide

---

## Issue Tracking

### Active Issues

- **[minmax-reformulation-spurious-variables.md](issues/minmax-reformulation-spurious-variables.md)** - Min/max reformulation
- **[parser-hyphens-in-equation-descriptions.md](issues/parser-hyphens-in-equation-descriptions.md)** - Parser enhancement
- **[parser-multi-dimensional-parameters-not-supported.md](issues/parser-multi-dimensional-parameters-not-supported.md)** - Parser limitation

### Completed Issues

See [issues/completed/](issues/completed/) directory for resolved issues.

---

## Process Documentation

- **[CHECKPOINT_TEMPLATES.md](process/CHECKPOINT_TEMPLATES.md)** - Sprint checkpoint templates
- **[AGENTS.md](development/AGENTS.md)** - Development agents and workflow
- **[ERROR_MESSAGES.md](development/ERROR_MESSAGES.md)** - Error message guidelines

---

## External Resources

### GitHub

- **Repository:** https://github.com/jeffreyhorn/nlp2mcp
- **Issues:** https://github.com/jeffreyhorn/nlp2mcp/issues
- **Discussions:** https://github.com/jeffreyhorn/nlp2mcp/discussions

### GAMS & PATH

- **GAMS Documentation:** https://www.gams.com/latest/docs/
- **PATH Solver:** https://pages.cs.wisc.edu/~ferris/path.html
- **MCP in GAMS:** https://www.gams.com/latest/docs/S_PATH.html

---

## Documentation by Use Case

### I want to...

**...get started quickly**
→ [README.md](../README.md) → [TUTORIAL.md](TUTORIAL.md)

**...understand all features**
→ [USER_GUIDE.md](USER_GUIDE.md)

**...fix a problem**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) → [FAQ.md](FAQ.md)

**...configure PATH solver**
→ [PATH_SOLVER.md](PATH_SOLVER.md)

**...understand limitations**
→ [LIMITATIONS.md](LIMITATIONS.md)

**...contribute code**
→ [CONTRIBUTING.md](../CONTRIBUTING.md) → [API docs](api/index.html)

**...understand the architecture**
→ [SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md) → [NLP2MCP_HIGH_LEVEL.md](concepts/NLP2MCP_HIGH_LEVEL.md)

**...see what changed**
→ [CHANGELOG.md](../CHANGELOG.md) → Sprint retrospectives

**...report a bug**
→ [GitHub Issues](https://github.com/jeffreyhorn/nlp2mcp/issues) → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Documentation Quality

This documentation index was last updated: **November 8, 2025**

**Coverage:**
- ✅ User documentation (Tutorial, User Guide, FAQ, Troubleshooting)
- ✅ Developer documentation (Architecture, API reference)
- ✅ Solver integration (PATH guide)
- ✅ Sprint plans and retrospectives
- ✅ Research and design documents
- ✅ Testing and validation reports

**Verification:**
- All links verified: November 8, 2025
- Sphinx builds successfully: Yes (144 warnings - docstring formatting)
- Examples tested: Yes (using `examples/` directory)
- Cross-linking complete: Yes

---

## Feedback

Found a broken link or missing documentation? 

- Open an issue: https://github.com/jeffreyhorn/nlp2mcp/issues
- Start a discussion: https://github.com/jeffreyhorn/nlp2mcp/discussions

---

**Last updated:** November 8, 2025
