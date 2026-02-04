# nlp2mcp Documentation Index

**Complete guide to all documentation resources**

Version: 1.1.0  
Last Updated: 2026-02-03

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

### GAMSLIB Testing & Validation

- **[GAMSLIB_TESTING.md](guides/GAMSLIB_TESTING.md)** - Comprehensive GAMSLIB testing guide
  - Full pipeline testing
  - Individual stage scripts
  - Database queries
  - Python API usage
  - CI/CD integration
  - Performance benchmarks
  - Troubleshooting
- **[GAMSLIB_USAGE.md](guides/GAMSLIB_USAGE.md)** - GAMSLIB usage workflows
  - Discovery and download
  - Database queries (CLI and Python)
  - Common workflows
- **[GAMSLIB_STATUS.md](testing/GAMSLIB_STATUS.md)** - Auto-generated status report
- **[FAILURE_ANALYSIS.md](testing/FAILURE_ANALYSIS.md)** - Auto-generated failure analysis

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

### Epic 3: GAMSLIB Validation Infrastructure

#### Sprint 17 (Current - Release v1.1.0)

- **[SPRINT_SCHEDULE.md](planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md)** - Sprint 17 detailed schedule
- **[SPRINT_LOG.md](planning/EPIC_3/SPRINT_17/SPRINT_LOG.md)** - Daily progress log
- **[KNOWN_UNKNOWNS.md](planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md)** - Research findings (27 unknowns)
- **[DOCUMENTATION_PLAN.md](planning/EPIC_3/SPRINT_17/DOCUMENTATION_PLAN.md)** - Documentation gaps and updates
- **[RELEASE_CHECKLIST.md](planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md)** - v1.1.0 release checklist

#### Sprint 16 (Reporting Infrastructure)

- **[SPRINT_SCHEDULE.md](planning/EPIC_3/SPRINT_16/SPRINT_SCHEDULE.md)** - Sprint 16 detailed schedule
- **[SPRINT_LOG.md](planning/EPIC_3/SPRINT_16/SPRINT_LOG.md)** - Daily progress log
- **[IMPROVEMENT_ROADMAP.md](planning/EPIC_3/SPRINT_16/IMPROVEMENT_ROADMAP.md)** - Prioritized improvements
- **[SPRINT_RETROSPECTIVE.md](planning/EPIC_3/SPRINT_16/SPRINT_RETROSPECTIVE.md)** - Sprint 16 retrospective

### Epic 2: Advanced Features & Hardening

#### Sprint 5 (Hardening & Release)

- **[PLAN.md](planning/SPRINT_5/PLAN.md)** - Sprint 5 detailed plan
- **[KNOWN_UNKNOWNS.md](planning/SPRINT_5/KNOWN_UNKNOWNS.md)** - Research findings

#### Sprint 4 (Advanced Features)

- **[PLAN.md](planning/SPRINT_4/PLAN.md)** - Sprint 4 plan
- **[RETROSPECTIVE.md](planning/SPRINT_4/RETROSPECTIVE.md)** - Sprint 4 retrospective

### Epic 1: Foundation

#### Sprint 3 (Testing & Validation)

- **[PLAN.md](planning/SPRINT_3/PLAN.md)** - Sprint 3 plan
- **[RETROSPECTIVE.md](planning/SPRINT_3/RETROSPECTIVE.md)** - Sprint 3 retrospective

#### Sprint 2 (Jacobian & Differentiation)

- **[PLAN.md](planning/SPRINT_2/PLAN.md)** - Sprint 2 plan
- **[RETROSPECTIVE.md](planning/SPRINT_2/RETROSPECTIVE.md)** - Sprint 2 retrospective

#### Sprint 1 (Foundation)

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

- **[v1.1.0 Release Notes](releases/v1.1.0.md)** - Current release (Sprint 17)
- **[v0.6.0 Release Notes](releases/v0.6.0.md)** - Previous release (Sprint 6)
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

This documentation index was last updated: **February 3, 2026**

**Coverage:**
- ✅ User documentation (Tutorial, User Guide, FAQ, Troubleshooting)
- ✅ Developer documentation (Architecture, API reference)
- ✅ Solver integration (PATH guide)
- ✅ GAMSLIB testing and validation guides
- ✅ Sprint plans and retrospectives (Epics 1-3)
- ✅ Research and design documents
- ✅ Testing and validation reports
- ✅ Automated status and failure reports

**Verification:**
- All links verified: February 3, 2026
- Sphinx builds successfully: Yes
- Examples tested: Yes (using `examples/` directory)
- Cross-linking complete: Yes

---

## Feedback

Found a broken link or missing documentation? 

- Open an issue: https://github.com/jeffreyhorn/nlp2mcp/issues
- Start a discussion: https://github.com/jeffreyhorn/nlp2mcp/discussions

---

**Last updated:** February 3, 2026
