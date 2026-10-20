# ISSUE #1775 — airsp, msm: translation timeout at 600 s (LP, multi-solve)

**GitHub:** [#1775](https://github.com/jeffreyhorn/nlp2mcp/issues/1775) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** P3 translate performance (Sprint 40 P3 routing note) · **Models:** `airsp`, `msm` (NLP-gated, `verified_convex`, admitted by rule Sprint 40 Day 3) · **Measured at:** `191ed91f` (the admission commit), uncontended (load ≈ 3–6)

## Fingerprint (reproduced)

Both parse, then hit the translate budget:

| model | translate | type | solves in source |
|---|---|---|---|
| `airsp` | **timeout at 600 s** (600.02) | LP | 3 (`alloch`, then `allocs` twice) |
| `msm` | **timeout at 600 s** (600.08) | LP | 5 (`msm`, five times) |

Prep Task 7 recorded the same. Neither is a load artifact: the run was one model at a time, with no other GAMS or pytest work on the machine.

## First step

Profile where the 600 s goes: parse → normalize → gradient → Jacobian → KKT assembly → emit. The `--diagnostics` / per-stage timing in `src/cli.py` names the stage. Then compare with the known translate-performance shapes:
- the #1385 dynamic-subset short-circuit;
- the S28 AD speed-ups that took `iswnm` from a 600 s timeout to 62 s.

⚠ **Both are multi-solve models.** Even once they translate, their comparison stays out of the headline until the reference question (Sprint 40 Day 3, P3) is settled.

**Not fixed in place.**
