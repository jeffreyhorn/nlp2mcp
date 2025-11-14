# nlp2mcp Roadmap

This document outlines planned features and enhancements for future releases.

## Sprint 7+ (Future Enhancements)

### Convexity Warning Suppression

**Status:** Deferred from Sprint 6 (Unknown 4.3)

**Description:**  
Add fine-grained control for suppressing specific convexity warnings beyond the current `--skip-convexity-check` flag.

**Proposed Features:**
- Per-warning-code suppression (e.g., `--skip-convexity W301,W302`)
- Configuration file support for suppression rules
- Inline suppression comments in GAMS code (e.g., `$suppress W301`)

**Rationale for Deferral:**  
The current `--skip-convexity-check` flag provides sufficient control for Sprint 6/v0.6.0. Users can disable all convexity warnings when needed. Fine-grained suppression is a quality-of-life enhancement that can be added based on user feedback.

**Implementation Complexity:** Low  
**User Impact:** Low (workaround available)  
**Target Sprint:** 7 or later (based on user demand)

---

## Future Feature Ideas

### Parser Enhancements
- Support for additional GAMS directives (`$if`, `$set`, etc.)
- Control flow constructs (`Loop`, `If`, `While`)
- External/user-defined functions

### Solver Integration
- Direct PATH solver integration
- Solution quality metrics
- Convergence diagnostics

### Performance Optimizations
- Parallel differentiation for large models
- Sparse matrix optimizations
- Memory usage improvements

### User Experience
- Interactive mode for step-by-step transformation
- Web-based UI for visualization
- VS Code extension for syntax highlighting

---

## Version History

See [CHANGELOG.md](../CHANGELOG.md) for detailed release history.
