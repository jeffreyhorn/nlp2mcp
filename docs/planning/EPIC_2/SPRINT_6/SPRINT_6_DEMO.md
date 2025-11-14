# Sprint 6 Demo Checklist

**Sprint:** Epic 2 - Sprint 6: Convexity Heuristics, Bug Fixes, GAMSLib, UX  
**Version:** v0.6.0  
**Demo Date:** TBD

## Pre-Demo Preparation

### Environment Setup
- [ ] Clean Python environment with nlp2mcp v0.6.0 installed
- [ ] Terminal window with clear screen and readable font
- [ ] Test models prepared in `examples/` directory
- [ ] Screen recording software ready (if needed)

### Test Data
- [ ] Convexity test models ready:
  - [ ] `examples/convex_qp.gms` - Convex quadratic program (0 warnings expected)
  - [ ] `examples/nonconvex_circle.gms` - Nonconvex with W301 warning
  - [ ] `examples/nonconvex_trig.gms` - Trigonometric with W302 warning
- [ ] GAMSLib models ingested (10 Tier 1 models)
- [ ] Conversion dashboard up to date

## Demo Script

### 1. Nested Min/Max Flattening (2 minutes)

**What to show:**
- AST transformation: `min(min(x,y),z)` → `min(x,y,z)`
- Reduction in auxiliary variables
- Semantic equivalence

**Commands:**
```bash
# Show before/after in code or terminal output
nlp2mcp examples/model_with_nested_min.gms -o output.gms -vv
```

**Key Points:**
- [ ] Explain nested min/max problem
- [ ] Show flattened output
- [ ] Highlight performance benefit (fewer aux variables)

### 2. Convexity Warnings (3 minutes)

**What to show:**
- Warning detection for nonconvex patterns
- Error codes (W301-W305)
- Documentation links
- Suppression flag

**Commands:**
```bash
# Show convexity warnings
nlp2mcp examples/nonconvex_circle.gms -o output.gms

# Show warning details
nlp2mcp examples/nonconvex_trig.gms -o output.gms -v

# Show suppression
nlp2mcp examples/nonconvex_circle.gms -o output.gms --skip-convexity-check
```

**Key Points:**
- [ ] Explain convexity detection (heuristics, not proofs)
- [ ] Show W301 (nonlinear equality), W302 (trig), etc.
- [ ] Navigate to error documentation
- [ ] Demonstrate suppression flag

### 3. GAMSLib Integration & Dashboard (3 minutes)

**What to show:**
- 10 GAMSLib models ingested
- Conversion dashboard with metrics
- Parse rate, error breakdown

**Commands:**
```bash
# Run ingestion (if not pre-run)
make ingest-gamslib

# Show dashboard
cat docs/status/GAMSLIB_CONVERSION_STATUS.md
```

**Key Points:**
- [ ] Explain GAMSLib benchmark suite
- [ ] Show dashboard sections (KPIs, model status, errors)
- [ ] Highlight Sprint 6 baseline (10% parse rate)
- [ ] Discuss future improvements

### 4. Error Message Integration (2 minutes)

**What to show:**
- Error code registry
- Comprehensive error documentation
- User-friendly error messages

**Commands:**
```bash
# Show error documentation
cat docs/errors/README.md | head -50

# Trigger an error (if possible)
nlp2mcp examples/invalid_model.gms 2>&1 | head -20
```

**Key Points:**
- [ ] Explain error code scheme (E0xx, W3xx, etc.)
- [ ] Show example error with code, description, fix
- [ ] Highlight documentation links

### 5. Overall UX Improvements (1 minute)

**What to show:**
- Updated CLI help
- Release notes
- Roadmap

**Commands:**
```bash
# Show help with new flags
nlp2mcp --help | grep -A2 convexity

# Show release notes
cat docs/releases/v0.6.0.md | head -30
```

**Key Points:**
- [ ] Summarize Sprint 6 achievements
- [ ] Mention 4 major feature areas
- [ ] Preview Sprint 7 plans

## Post-Demo Q&A Preparation

### Expected Questions

**Q: Are convexity warnings always accurate?**  
A: No, they are conservative heuristics. May produce false positives but never false negatives. Document as warnings, not errors.

**Q: What's the GAMSLib parse rate target?**  
A: Sprint 6 baseline is 10% (1/10 models). Sprint 7 target is 30%+ with parser improvements.

**Q: Can I suppress specific convexity warnings?**  
A: Not yet - Sprint 6 has all-or-nothing `--skip-convexity-check`. Fine-grained suppression is planned for Sprint 7+ (see roadmap).

**Q: What breaking changes in v0.6.0?**  
A: None. All changes are backward-compatible additions.

**Q: When is v0.6.0 release?**  
A: After Sprint 6 Day 10 (sprint review and release prep).

## Demo Success Criteria

- [ ] All 5 demo sections completed without errors
- [ ] Key features clearly explained
- [ ] Audience questions answered
- [ ] Demo artifacts saved (recordings, terminal outputs)
- [ ] Feedback collected for future improvements

## Backup Plans

### If convexity detection fails:
- Show pre-recorded terminal output
- Walk through source code in `src/diagnostics/convexity/`

### If GAMSLib dashboard outdated:
- Re-run `make ingest-gamslib` (2-3 minutes)
- Have screenshot backup ready

### If terminal issues:
- Use pre-prepared slides with code snippets
- Share documentation links for offline review

## Demo Artifacts to Save

- [ ] Terminal recordings (asciinema or video)
- [ ] Output files from demo runs
- [ ] Screenshots of dashboard and error docs
- [ ] Feedback notes
- [ ] Follow-up action items

---

**Last Updated:** Sprint 6 Day 8  
**Prepared By:** UX Team  
**Review Status:** Pending review by Full Team
