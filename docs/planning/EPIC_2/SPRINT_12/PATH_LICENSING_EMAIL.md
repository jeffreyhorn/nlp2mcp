# PATH Solver Licensing Email Template

**Purpose:** Request clarification on PATH solver academic license terms for GitHub Actions CI usage  
**Date Created:** 2025-11-30  
**Task:** Sprint 12 Prep Task 6 - Draft PATH Licensing Email Template  
**Status:** Ready to send on Sprint 12 Day 1

---

## Executive Summary

This document provides a professional email template requesting PATH solver licensing clarification from Dr. Michael C. Ferris. **Key unknown:** Whether PATH academic license permits automated testing in cloud CI environments (GitHub Actions).

**Timeline:** Email response may take 1-4 weeks (async process). Sending early in Sprint 12 maximizes response window.

**Follow-up Scenarios:**
- ✅ **Approved:** Implement PATH in CI (Sprint 12 Days 7-8, 3-4h effort)
- ⚠️ **Denied:** Continue with IPOPT, document decision (Sprint 12 Day 7, 1h effort)
- 🔍 **No response by Day 7:** Defer PATH to Sprint 13, proceed with IPOPT
- 🔧 **Self-hosted required:** Evaluate feasibility (cost, maintenance, security)

---

## Table of Contents

1. [Contact Information](#contact-information)
2. [Email Template](#email-template)
3. [Follow-Up Scenarios](#follow-up-scenarios)
4. [Timeline Expectations](#timeline-expectations)
5. [Background Context](#background-context)
6. [Alternative Solutions](#alternative-solutions)

---

## Contact Information

**Recipient:** Dr. Michael C. Ferris  
**Email:** ferris@cs.wisc.edu  
**Affiliation:** Computer Sciences Department, University of Wisconsin-Madison  
**Role:** PATH Solver Maintainer and Primary Author  
**Website:** https://pages.cs.wisc.edu/~ferris/path.html

**Verification Status:** ✅ Contact information verified current as of 2025-11-30

---

## Email Template

**Subject:** PATH Solver Academic License - GitHub Actions CI Usage Clarification

---

Dear Dr. Ferris,

I am writing to seek clarification on the PATH solver academic license terms for use in continuous integration (CI) environments.

**Project Background:**

Our project, nlp2mcp, is an open-source academic tool that converts GAMS NLP (Nonlinear Programming) models to MCP (Mixed Complementarity Problem) format. The project is:
- Hosted on GitHub: https://github.com/jeffreyhorn/nlp2mcp
- Licensed under MIT (open source, non-commercial)
- Academic research project for GAMS model transformation

**Current Usage:**

We currently use IPOPT for MCP validation in our GitHub Actions CI workflows. However, we would like to use PATH for more accurate validation, as it is the reference solver for GAMS MCP models and provides superior complementarity handling.

**Specific Questions:**

The PATH academic license terms (https://pages.cs.wisc.edu/~ferris/path.html) state that "A new license string will be provided in December of each year" for academic use, but do not explicitly address cloud CI usage. Could you please clarify:

1. **Does the PATH academic license permit use in GitHub Actions (cloud CI runners)?**
   - GitHub Actions runs on shared cloud infrastructure (Microsoft Azure VMs)
   - Not personal machines, but still academic research use case

2. **If so, are there restrictions on CI frequency?**
   - Our use case: ~100 runs/month (per-PR validation + nightly builds)
   - Each run: 4-5 small MCP smoke tests (<50 variables each)
   - Total annual compute: ~1,200 solver invocations

3. **Is use in public open-source repositories permitted under academic licensing?**
   - Repository is public (educational purposes)
   - No commercial use, purely validation of research software
   - CI workflow configurations are public (transparent usage)

**Alternative Options (if cloud CI not permitted):**

If GitHub Actions is not permitted under academic licensing, we have several alternatives:
- Continue with IPOPT as our CI solver (acceptable accuracy for smoke tests)
- Set up self-hosted GitHub Actions runner on a licensed university machine
- Use PATH free version (300 variable / 2,000 nonzero limit is sufficient for our smoke tests)

We would appreciate written confirmation for our documentation, as this will guide our Sprint 12 implementation decisions.

**Timeline:**

Our Sprint 12 development cycle (December 2-13, 2025) would benefit from clarification, but we understand this may take time. We have IPOPT as a fallback and can defer PATH integration if needed.

Please let us know if you need any additional information about our use case or project.

Thank you for your time and for maintaining the PATH solver.

Best regards,

[Your Name]  
[Your Affiliation]  
nlp2mcp Development Team  
GitHub: https://github.com/jeffreyhorn/nlp2mcp

---

## Follow-Up Scenarios

### Scenario A: Approved (CI Use Permitted)

**Response:** "PATH academic license permits GitHub Actions usage under academic research terms."

**Sprint 12 Actions (Days 7-8, 3-4h):**
1. Add GAMS/PATH installation to nightly CI workflow (1h)
   ```yaml
   # .github/workflows/path-smoke-tests-nightly.yml
   - name: Install GAMS with PATH
     run: |
       wget https://d37drm4t2jghv5.cloudfront.net/distributions/latest/linux/linux_x64_64_sfx.exe
       chmod +x linux_x64_64_sfx.exe
       ./linux_x64_64_sfx.exe -q -d /opt/gams
       echo "/opt/gams" >> $GITHUB_PATH
   ```
2. Configure PATH academic license in CI (0.5h)
   - Store license string in GitHub Secrets
   - Set up license file in workflow
3. Migrate existing PATH tests to CI (1h)
   - Remove `skipif` decorators from `tests/validation/test_path_solver.py`
   - Update test documentation
4. Run validation suite (0.5h)
   - Verify all 4 smoke tests pass
   - Compare PATH vs IPOPT results
5. Documentation (1h)
   - Update README.md with PATH CI usage
   - Document license renewal process (annual December renewal)

**Deliverables:**
- ✅ PATH installed in nightly CI workflow
- ✅ PATH smoke tests enabled (4-test suite)
- ✅ PATH vs IPOPT accuracy comparison documented
- ✅ License renewal process documented

**Success Criteria:**
- All PATH smoke tests pass in CI
- PATH and IPOPT solutions agree within 1% relative error
- Annual license renewal process documented for future maintenance

---

### Scenario B: Denied (CI Use Not Permitted)

**Response:** "PATH academic license does not permit cloud CI usage. Please use self-hosted runner or free version."

**Sprint 12 Actions (Day 7, 1h):**
1. Document licensing decision (0.5h)
   - Create `docs/decisions/PATH_LICENSING_DECISION.md`
   - Explain why PATH not used in CI
   - Reference IPOPT as approved alternative
2. Update test documentation (0.5h)
   - Keep `skipif` decorators in PATH tests
   - Document that PATH tests run locally only
   - Add note about IPOPT vs PATH accuracy (<1% difference)

**Deliverables:**
- ✅ Decision document created
- ✅ Test documentation updated
- ✅ IPOPT confirmed as CI solver

**Success Criteria:**
- Decision clearly documented for future reference
- IPOPT smoke tests continue to run in CI
- No PATH licensing violations

**Long-term Options:**
- Defer PATH to Sprint 13+ if self-hosted runner feasible
- Accept IPOPT as sufficient for CI validation

---

### Scenario C: No Response by Day 7

**Response:** (No email response within Sprint 12 timeline)

**Sprint 12 Actions (Day 7, 0.5h):**
1. Defer PATH integration to Sprint 13 (0.5h)
   - Document in Sprint 12 retrospective
   - Add to Sprint 13 backlog (conditional on response)
   - Continue with IPOPT for Sprint 12

**Deliverables:**
- ✅ Deferral documented in retrospective
- ✅ Sprint 13 backlog updated

**Success Criteria:**
- No blocking issues for Sprint 12
- IPOPT continues to provide CI validation

**Follow-up Actions:**
- Send reminder email after Sprint 12 (Week 3)
- Escalate to alternative contact if no response after 4 weeks
- Accept IPOPT as permanent solution if no response after 8 weeks

---

### Scenario D: Self-Hosted Runner Required

**Response:** "PATH academic license permits use, but only on licensed machines (not cloud CI). Please use self-hosted runner."

**Sprint 12 Actions (Day 7-8, 2-3h):**
1. Evaluate self-hosted runner feasibility (1-2h)
   - **Requirements:**
     - Dedicated machine with GAMS/PATH installed
     - 24/7 uptime (or accept occasional CI failures)
     - Secure network access (firewall configuration)
     - Maintenance plan (security updates, monitoring)
   - **Costs:**
     - Machine: University server (free) or cloud VM ($50-100/month)
     - Maintenance: ~2h/month (security patches, monitoring)
     - Downtime risk: High (single point of failure)
   - **Security:**
     - Self-hosted runners can access repository secrets (risk)
     - Need network isolation and least-privilege access
2. Decision: Implement or defer (0.5h)
   - **If feasible:** Set up self-hosted runner (Sprint 12 Day 8-9, 3-4h)
   - **If not feasible:** Document decision, defer PATH, continue IPOPT (0.5h)
3. Documentation (0.5h)
   - Document self-hosted runner setup if implemented
   - Document deferral decision if not feasible

**Deliverables:**
- ✅ Feasibility evaluation completed
- ✅ Decision documented (implement or defer)
- ✅ Self-hosted runner operational (if implemented) OR deferral rationale documented

**Success Criteria (if implemented):**
- Self-hosted runner passes security review
- PATH tests run successfully on self-hosted runner
- Monitoring and maintenance plan in place

**Success Criteria (if deferred):**
- Decision clearly justified with cost/benefit analysis
- IPOPT confirmed as sufficient alternative

---

## Timeline Expectations

### Response Timeline Probability

| Timeframe | Probability | Sprint 12 Impact |
|-----------|-------------|------------------|
| **1-3 days** | 10% | ✅ Can implement PATH in Sprint 12 |
| **4-7 days** | 30% | ✅ Can implement PATH in Sprint 12 (tight timeline) |
| **1-2 weeks** | 40% | ⚠️ May defer PATH to Sprint 13 |
| **2-4 weeks** | 15% | ❌ Defer PATH to Sprint 13 |
| **No response** | 5% | ❌ Defer PATH indefinitely, accept IPOPT |

**Expected Scenario:** Response within 1-2 weeks (70% probability)

### Sprint 12 Decision Points

**Day 1:** Send email immediately  
**Day 3:** Check for response (early response)  
**Day 5:** Check for response (mid-sprint)  
**Day 7:** **CHECKPOINT** - Make final decision:
- If approved: Implement PATH (Days 7-8)
- If denied: Document decision (Day 7)
- If no response: Defer to Sprint 13 (Day 7)

**Day 10:** Sprint 12 complete regardless of PATH status (IPOPT fallback ensures no blocking)

---

## Background Context

### Why PATH Matters

**PATH vs IPOPT Comparison:**

| Feature | PATH | IPOPT |
|---------|------|-------|
| **Complementarity** | Native MCP solver | Reformulated as NLP (Fischer-Burmeister) |
| **Accuracy** | Reference implementation | <1% relative error vs PATH |
| **Speed (MCP)** | Fast (~0.1s for small MCP) | Medium (~0.2s for small MCP) |
| **License** | Proprietary (academic free) | Open source (EPL) |
| **CI-Friendly** | ❓ **UNCLEAR** | ✅ **YES** |

**Sprint 11 Findings:**
- IPOPT provides 90%+ of PATH accuracy for small MCPs
- IPOPT sufficient for smoke testing (detect gross errors)
- PATH preferred for comprehensive validation (reference solver)

**Use Case: Smoke Tests**
- 4 test cases: trivial 2×2 MCP, hansmcp.gms, infeasible MCP, unbounded MCP
- All test cases <50 variables (well within PATH free limit: 300 variables)
- Test frequency: ~100 runs/month (nightly + per-PR)

### Research Done in Sprint 11

**Sprint 11 Task 8:** PATH Smoke Test Integration Research
- Document: `docs/planning/EPIC_2/SPRINT_11/path_smoke_test_integration.md`
- **Key Finding:** PATH licensing UNCLEAR for CI/cloud usage
- **Decision:** Defer PATH to Sprint 12, prototype IPOPT alternative
- **Action:** Contact PATH maintainer for clarification

**IPOPT Prototype (Sprint 11):**
- ✅ IPOPT smoke tests implemented and passing
- ✅ Accuracy validation: <1% error vs PATH on 3 GAMSLib models
- ✅ CI integration: 30s installation overhead (vs 2min for GAMS/PATH)
- ✅ Nightly workflow operational

### Why We Need Written Clarification

**Legal/Compliance Reasons:**
1. Academic license terms silent on cloud CI usage
2. GitHub Actions runs on commercial cloud infrastructure (Microsoft Azure)
3. Repository is public (open source, but licensing still applies)
4. Annual renewal required (need to ensure CI doesn't violate terms)

**Risk Mitigation:**
- Written confirmation prevents future licensing disputes
- Documents acceptable use for CI configuration
- Provides evidence of good-faith effort to comply with terms

---

## Alternative Solutions

### Option 1: IPOPT (Current Approach - No Licensing Issues)

**Pros:**
- ✅ Open source (EPL license) - no restrictions
- ✅ Already implemented and working in CI
- ✅ Fast installation (~30s vs 2min for PATH)
- ✅ Sufficient accuracy for smoke tests (<1% error vs PATH)
- ✅ No annual license renewal required

**Cons:**
- ⚠️ Not reference solver (PATH is GAMS standard)
- ⚠️ MCP reformulated as NLP (less "native" than PATH)
- ⚠️ 2× slower solve time (0.2s vs 0.1s for PATH)

**Verdict:** ✅ **ACCEPTABLE FALLBACK** - Continue if PATH unavailable

---

### Option 2: PATH Free Version (300 var / 2,000 nonzero limit)

**Pros:**
- ✅ No licensing questions (free version has no restrictions)
- ✅ Sufficient for smoke tests (<50 variables each)
- ✅ Reference PATH solver (not IPOPT alternative)

**Cons:**
- ⚠️ Cannot test larger models (scarfmcp.gms: >300 variables)
- ⚠️ Still requires GAMS installation (2min CI overhead)
- ⚠️ Size limit may block future comprehensive validation

**Verdict:** ⚠️ **VIABLE IF ACADEMIC LICENSE DENIED** - Covers smoke tests but limits future expansion

---

### Option 3: Self-Hosted GitHub Actions Runner

**Pros:**
- ✅ Full PATH access on licensed machine
- ✅ No cloud licensing concerns
- ✅ Fast (PATH pre-installed, no download overhead)
- ✅ Controlled environment

**Cons:**
- ❌ Maintenance burden (runner uptime, security, updates)
- ❌ Single point of failure (if runner down, CI blocks)
- ❌ Security risks (self-hosted runners access repo secrets)
- ❌ Cost (machine hosting, monitoring, maintenance)

**Estimated Effort:**
- Setup: 3-4 hours (install runner, configure security)
- Maintenance: 2h/month (security patches, monitoring)
- Downtime: 5-10% (runner restarts, network issues)

**Verdict:** ⚠️ **HIGH MAINTENANCE** - Only if PATH critical and cloud CI denied

---

### Option 4: Defer PATH Indefinitely (IPOPT-Only)

**Pros:**
- ✅ Zero licensing complexity
- ✅ Zero maintenance overhead
- ✅ Already implemented and working
- ✅ Sufficient for current needs

**Cons:**
- ⚠️ Not using "reference" solver
- ⚠️ May miss edge cases where IPOPT/PATH disagree

**Verdict:** ✅ **ACCEPTABLE IF NO PATH RESPONSE** - IPOPT proven sufficient for smoke tests

---

## Summary

**Email Template:** Ready to send on Sprint 12 Day 1  
**Contact:** ferris@cs.wisc.edu (verified current)  
**Expected Response Time:** 1-2 weeks (70% probability)  
**Sprint 12 Checkpoint:** Day 7 - decide based on response status

**Follow-up Decision Tree:**
```
PATH Licensing Response?
├─ ✅ "CI use permitted"
│   └─ Sprint 12 Days 7-8: Implement PATH in nightly CI (3-4h)
│
├─ ⚠️ "CI use NOT permitted (cloud)"
│   ├─ Option A: Self-hosted runner (if feasible, 3-4h setup)
│   └─ Option B: Continue IPOPT only (document decision, 1h)
│
├─ 🔍 "No response by Day 7"
│   └─ Defer PATH to Sprint 13, continue IPOPT (0.5h)
│
└─ 🔧 "Self-hosted runner required"
    ├─ Evaluate feasibility (1-2h)
    ├─ If feasible: Set up runner (3-4h)
    └─ If not feasible: Continue IPOPT, document decision (1h)
```

**Key Insight:** IPOPT fallback ensures Sprint 12 is not blocked by PATH licensing uncertainty. Email is sent early to maximize response window, but lack of response does not impact sprint success.

---

## Appendix: Quick Copy Template

**For easy copying when sending email:**

```
Subject: PATH Solver Academic License - GitHub Actions CI Usage Clarification

Dear Dr. Ferris,

I am writing to seek clarification on the PATH solver academic license terms for use in continuous integration (CI) environments.

**Project Background:**
Our project, nlp2mcp, is an open-source academic tool that converts GAMS NLP models to MCP format. The project is hosted on GitHub (https://github.com/jeffreyhorn/nlp2mcp) under MIT license and is a non-commercial academic research project.

**Current Usage:**
We currently use IPOPT for MCP validation in our GitHub Actions CI workflows. However, we would like to use PATH for more accurate validation, as it is the reference solver for GAMS MCP models.

**Specific Questions:**
The PATH academic license terms (https://pages.cs.wisc.edu/~ferris/path.html) do not explicitly address cloud CI usage. Could you please clarify:

1. Does the PATH academic license permit use in GitHub Actions (cloud CI runners on Microsoft Azure)?
2. Are there restrictions on CI frequency? (Our use case: ~100 runs/month, 4-5 small MCP smoke tests per run)
3. Is use in public open-source repositories permitted under academic licensing?

**Alternative Options (if cloud CI not permitted):**
- Continue with IPOPT as our CI solver
- Set up self-hosted GitHub Actions runner on a licensed university machine
- Use PATH free version (300 variable limit is sufficient for our smoke tests)

We would appreciate written confirmation for our documentation.

**Timeline:**
Our Sprint 12 development cycle (December 2-13, 2025) would benefit from clarification, but we have IPOPT as a fallback and can defer PATH integration if needed.

Thank you for your time and for maintaining the PATH solver.

Best regards,
[Your Name]
[Your Affiliation]
nlp2mcp Development Team
GitHub: https://github.com/jeffreyhorn/nlp2mcp
```

---

**Document Status:** ✅ Ready for Use  
**Next Action:** Send email on Sprint 12 Day 1  
**Owner:** Sprint 12 execution team  
**Review Status:** Approved for sending
