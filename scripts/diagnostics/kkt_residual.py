#!/usr/bin/env python3
"""KKT-residual verification harness (Sprint 28 Priority 9 / PR27).

Formalizes Sprint 27's GDX warm-from-good-optimum experiment into the standard
Case-(a/b/c) emit-bug-vs-non-convexity discriminator.

**Architecture A (chosen Sprint 28 Day 1):** the harness *reuses* the production
``--nlp-presolve`` emit for the warm-start. The Day-1 finding (PR24) corrected the
design doc's §2.66 premise — ``_emit_nlp_presolve`` (``src/emit/emit_gams.py``)
already loads the NLP duals into the MCP multipliers (``nu_<eq>.l = eq.m``,
``lam_<eq>.l = abs(eq.m)``, ``piL_*``/``piU_*`` from variable marginals), so the
harness does not re-derive the dual transfer via ``build_complementarity_pairs``.
It emits the MCP with ``--nlp-presolve`` (primal + dual warm-start), rewrites the
``Solve`` to an ``iterlim=0`` residual evaluation, and reads the per-row residuals.

See ``docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md``.

Build status: Day 2 — full pipeline. Emits the warm-started MCP, builds the
residual-only variant (``nu`` sign-corrected, ``iterlim=0``, ``execute_unload``),
runs it through GAMS, reads per-row residuals via ``gdxdump``, runs the §2
self-check + the §3 Case-(a/b/c) verdict (relative residual; optional cold-start
for the a-vs-c split), and writes the human + ``--json`` report. ``--gdx`` skips
the embedded NLP solve via ``execute_loadpoint``. Day-2 self-validation found
launch is **Case c** (residual ≈ 0 but the cold non-presolve MCP is Locally
Infeasible), not Case a as the design's §7 table assumed; Day-3 validates camshape
→ Case b and cclinpts → Case c and picks a clean Case-a model.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TOL_DEFAULT = 1e-6  # absolute floor for the §2 consistency self-check
REL_TOL_DEFAULT = 1e-3  # relative stationarity-residual threshold (Day-2 verdict)
FEAS_TOL_DEFAULT = 1e-4  # gross-infeasibility floor for the complementarity guard
DEFAULT_NLP_SOLVER = "CONOPT"
MCP_MODEL_NAME = "mcp_model"

# Row-name prefixes the emitter uses (src/kkt/naming.py).
STAT_PREFIX = "stat_"
COMP_PREFIX = "comp_"

# A multiplier warm-start statement, e.g. `nu_diweight.l(s) = diweight.m(s);`.
_MULT_RE = re.compile(r"^(nu|lam|piL|piU)_\w+\.l\b.*=.*;")

# A free-equality-multiplier warm-start: `nu_<eq>.l(<idx>) = <rhs>;`. The Day-2
# residual check negates the rhs (the production `nu = eq.m` is sign-flipped vs
# the emitted stationarity convention — see the design §2 Day-2 correction).
_NU_TRANSFER_RE = re.compile(r"^(nu_\w+\.l(?:\([^)]*\))?)\s*=\s*([^;]+);", re.MULTILINE)


@dataclass
class DualTransfer:
    """The multiplier warm-start statements the ``--nlp-presolve`` emit produced.

    Architecture A: the harness extracts (rather than re-derives) these from the
    emitted ``*_mcp_presolve.gms`` to confirm the production transfer covers the
    four multiplier classes before trusting any residual.
    """

    nu: list[str] = field(default_factory=list)  # equality multipliers (free)
    lam: list[str] = field(default_factory=list)  # inequality (>= 0, abs of .m)
    piL: list[str] = field(default_factory=list)  # lower-bound multipliers
    piU: list[str] = field(default_factory=list)  # upper-bound multipliers

    @property
    def total(self) -> int:
        return len(self.nu) + len(self.lam) + len(self.piL) + len(self.piU)

    @property
    def is_empty(self) -> bool:
        return self.total == 0

    def summary(self) -> str:
        return (
            f"nu={len(self.nu)} lam={len(self.lam)} "
            f"piL={len(self.piL)} piU={len(self.piU)} (total {self.total})"
        )


def extract_dual_transfer(mcp_presolve_text: str) -> DualTransfer:
    """Extract the multiplier warm-start statements from a ``--nlp-presolve`` emit.

    Pure string parse (no GAMS): scans for ``nu_*.l = … ;`` / ``lam_*.l = … ;`` /
    ``piL_*.l = … ;`` / ``piU_*.l = … ;`` assignments. This is the harness's
    dual-transfer *verification* layer under Architecture A — it confirms the
    production transfer is present (an empty result is a flag, cf. cesam's empty
    ``nu_*`` block found at Day 0).
    """
    transfer = DualTransfer()
    bucket = {
        "nu": transfer.nu,
        "lam": transfer.lam,
        "piL": transfer.piL,
        "piU": transfer.piU,
    }
    for raw in mcp_presolve_text.splitlines():
        line = raw.strip()
        m = _MULT_RE.match(line)
        if m is not None:
            bucket[m.group(1)].append(line)
    return transfer


def make_residual_only(mcp_text: str, model_name: str = MCP_MODEL_NAME) -> str:
    """Rewrite the emitted MCP so PATH evaluates residuals at the warm-start point
    without iterating: insert ``<model>.iterlim = 0;`` immediately before the
    ``Solve <model> using MCP;`` statement.

    ``iterlim = 0`` makes PATH report the system value at the start point (the
    transferred NLP KKT point) rather than solving — the residual-only evaluation
    the Case-(a/b/c) verdict reads. Raises ``ValueError`` if the Solve isn't found.
    """
    solve_re = re.compile(
        rf"^([ \t]*)Solve\s+{re.escape(model_name)}\s+using\s+MCP\s*;",
        re.IGNORECASE | re.MULTILINE,
    )

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1)
        return f"{indent}{model_name}.iterlim = 0;\n{match.group(0)}"

    new_text, n = solve_re.subn(repl, mcp_text)
    if n == 0:
        raise ValueError(
            f"no `Solve {model_name} using MCP;` statement found to rewrite "
            "for residual-only (iterlim=0) evaluation"
        )
    return new_text


def apply_residual_sign_correction(mcp_text: str) -> str:
    """Negate the free-equality-multiplier (`nu_*`) warm-start for the residual check.

    The production `--nlp-presolve` emit loads `nu_<eq>.l = eq.m`, but the GAMS
    equality marginal is sign-flipped relative to the emitted stationarity row's
    `nu` convention (design §2, Day-2 correction). Loading `+eq.m` leaves the
    stationarity rows non-zero even at a valid KKT point (launch: `stat_aweight`
    ≈ 2·|eq.m|); loading `-eq.m` drives them to ~1e-12. Only the *free* multiplier
    `nu` is sign-ambiguous — `lam`/`piL`/`piU` load as non-negative magnitudes with
    the sign carried in the emitted coefficient, so they are left untouched.

    Idempotency note: this negates the rhs of each `nu_*.l = …;` once. It is meant
    to run exactly once on a freshly emitted presolve MCP.
    """

    def negate(match: re.Match[str]) -> str:
        return f"{match.group(1)} = -({match.group(2).strip()});"

    return _NU_TRANSFER_RE.sub(negate, mcp_text)


def inject_residual_unload(mcp_text: str, gdx_path: str, model_name: str = MCP_MODEL_NAME) -> str:
    """Append `execute_unload '<gdx>';` immediately after the MCP `Solve` so the
    post-solve equation levels (= the per-row residuals at `iterlim=0`) are written
    to a GDX the harness reads back with `gdxdump`.

    Must be applied to text that already contains the (residual-only) Solve; raises
    ``ValueError`` if the Solve isn't found.
    """
    solve_re = re.compile(
        rf"^([ \t]*)(Solve\s+{re.escape(model_name)}\s+using\s+MCP\s*;)",
        re.IGNORECASE | re.MULTILINE,
    )

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1)
        return f"{indent}{match.group(2)}\n{indent}execute_unload '{gdx_path}';"

    new_text, n = solve_re.subn(repl, mcp_text)
    if n == 0:
        raise ValueError(
            f"no `Solve {model_name} using MCP;` statement found to append "
            "`execute_unload` after"
        )
    return new_text


def classify_consistency(
    constraint_residuals: dict[str, float], tol: float = TOL_DEFAULT
) -> str | None:
    """Primitive offending-row test for the §2 self-check.

    Returns ``"dual_transfer_inconsistent"`` if any residual is non-finite or
    exceeds ``tol`` in absolute value, else ``None``. The *row selection* the
    real self-check applies (which rows count, fail-closed-on-NaN, gross
    complementarity infeasibility, excluding objective-definitional rows — see
    the design §2 Day-2 correction) lives in :func:`check_dual_transfer`; this is
    the underlying threshold primitive it builds on.

    Fails **closed** on non-finite residuals: a ``NaN``/``inf`` row (e.g. from a
    div-by-zero during residual evaluation, cf. korcge #1439) is offending —
    ``abs(nan) > tol`` is ``False``, so it would otherwise slip through.
    """
    offending = {
        k: v for k, v in constraint_residuals.items() if not math.isfinite(v) or abs(v) > tol
    }
    return "dual_transfer_inconsistent" if offending else None


@dataclass(frozen=True)
class RowResidual:
    """One equation row at the warm-start point, from the GDX ``Val``/``Lower``/
    ``Upper`` fields (``gdxdump … CSVAllFields``).

    ``val`` is the equation level (activity). GAMS moves a constraint's *constant*
    term to the ``=`` bound: ``stat_r .. F =E= 0`` → ``val=F, lower=upper=0``;
    ``50000 - vt =G= 0`` → ``val=-vt, lower=-50000, upper=+inf``. So the residual is
    ``val`` *relative to its bounds*, not ``val`` itself — the Day-2 fix that
    dissolved the apparent ``costdef``/``dweight`` discrepancies (they have
    ``val == lower == upper`` → residual 0). ``kind`` is ``"stationarity"`` /
    ``"complementarity"`` / ``"equality"``.
    """

    name: str
    index: tuple[str, ...]
    val: float
    lower: float
    upper: float
    kind: str

    @classmethod
    def from_fields(
        cls, name: str, index: tuple[str, ...], val: float, lower: float, upper: float
    ) -> RowResidual:
        return cls(name, index, val, lower, upper, row_kind(name))

    @classmethod
    def equality(cls, name: str, index: tuple[str, ...], residual: float) -> RowResidual:
        """Test/convenience builder for an ``=E=``-style row (``lower=upper=0`` so
        ``signed_residual == residual``); ``kind`` from the name prefix."""
        return cls(name, index, residual, 0.0, 0.0, row_kind(name))

    @classmethod
    def inequality(
        cls, name: str, index: tuple[str, ...], val: float, lower: float, upper: float
    ) -> RowResidual:
        """Test/convenience builder for a ``=g=``/``=l=`` (complementarity) row."""
        return cls(name, index, val, lower, upper, "complementarity")

    @property
    def label(self) -> str:
        return f"{self.name}({','.join(self.index)})" if self.index else self.name

    @property
    def is_equality(self) -> bool:
        """Two-sided (``=E=``-style) row: a finite, equal lower/upper bound."""
        return math.isfinite(self.lower) and self.lower == self.upper

    @property
    def signed_residual(self) -> float:
        """The signed residual for an equality-type row (``val - bound``); for an
        inequality row, the bare activity ``val`` (sign-carrying, for display)."""
        return self.val - self.lower if self.is_equality else self.val

    @property
    def infeasibility(self) -> float:
        """Bound-violation magnitude (``≥ 0``): ``max(lower-val, val-upper, 0)`` with
        ``±inf`` bounds ignored. For a stationarity/equality row (``lower==upper``)
        this is ``|val - bound|``; for a ``=g=`` row it is the constraint breach
        (``0`` when the activity is within bounds). Propagates a non-finite ``val``."""
        if not math.isfinite(self.val):
            return self.val
        lo_v = (self.lower - self.val) if math.isfinite(self.lower) else 0.0
        up_v = (self.val - self.upper) if math.isfinite(self.upper) else 0.0
        return max(lo_v, up_v, 0.0)


def row_kind(name: str) -> str:
    """Classify an equation row by its emitted name prefix (src/kkt/naming.py)."""
    if name.startswith(STAT_PREFIX):
        return "stationarity"
    if name.startswith(COMP_PREFIX):
        return "complementarity"
    return "equality"


def parse_gdxdump_csv(csv_text: str) -> dict[tuple[str, ...], float]:
    """Parse one symbol's ``gdxdump … format=csv`` output into ``{index: value}``.

    The CSV header is the domain labels then ``"Val"`` (e.g. ``"s","Val"``), or
    just ``"Val"`` for a scalar. Each data row is ``"idx0",…,"idxN",<number>``.
    Non-finite GAMS tokens (``NA``/``INF``/``-INF``/``UNDF``/``EPS``) map to the
    corresponding float so the fail-closed self-check sees them. A scalar yields
    ``{(): value}``. Blank/garbage lines are skipped.
    """
    out: dict[tuple[str, ...], float] = {}
    lines = [ln for ln in csv_text.splitlines() if ln.strip()]
    if not lines:
        return out
    # Drop the header row (it ends with the "Val" column label).
    body = lines[1:] if lines[0].rstrip().endswith('"Val"') else lines
    for line in body:
        fields = _split_csv_row(line)
        if not fields:
            continue
        value = _gams_number(fields[-1])
        if value is None:
            continue
        index = tuple(fields[:-1])
        out[index] = value
    return out


def parse_gdxdump_allfields(csv_text: str) -> dict[tuple[str, ...], tuple[float, float, float]]:
    """Parse one equation symbol's ``gdxdump … format=csv CSVAllFields`` output into
    ``{index: (val, lower, upper)}``.

    The header is ``[<domain>,] "Val","Marginal","Lower","Upper","Scale"``; each data
    row ends with those five values. The constant term of a constraint lives in
    ``Lower``/``Upper`` (not ``Val``), so the residual is computed from all three
    (see :class:`RowResidual`). Non-finite tokens propagate; a scalar yields ``{(): …}``.
    """
    out: dict[tuple[str, ...], tuple[float, float, float]] = {}
    lines = [ln for ln in csv_text.splitlines() if ln.strip()]
    if not lines:
        return out
    body = lines[1:] if lines[0].rstrip().endswith('"Scale"') else lines
    for line in body:
        fields = _split_csv_row(line)
        if len(fields) < 5:
            continue
        val = _gams_number(fields[-5])  # Val, Marginal, Lower, Upper, Scale
        lower = _gams_number(fields[-3])
        upper = _gams_number(fields[-2])
        if val is None or lower is None or upper is None:
            continue
        index = tuple(fields[:-5])
        out[index] = (val, lower, upper)
    return out


def _split_csv_row(line: str) -> list[str]:
    """Split a gdxdump CSV row into fields using the standard CSV dialect, so quoted
    GAMS index labels containing commas or escaped quotes parse correctly (gdxdump
    quotes index labels and leaves numeric values unquoted)."""
    try:
        return next(csv.reader([line]))
    except StopIteration:
        return []


def _gams_number(token: str) -> float | None:
    """Parse a GAMS/gdxdump numeric token, mapping the special values so the
    fail-closed self-check can see non-finite residuals."""
    t = token.strip().strip('"')
    specials = {
        "NA": math.nan,
        "UNDF": math.nan,
        "INF": math.inf,
        "+INF": math.inf,
        "-INF": -math.inf,
        "EPS": 0.0,
    }
    if t.upper() in specials:
        return specials[t.upper()]
    try:
        return float(t)
    except ValueError:
        return None


def dual_scale(multiplier_values: list[float]) -> float:
    """IPOPT-style dual-infeasibility scale for the relative residual: the largest
    transferred-multiplier magnitude, floored at 1.0 (design §3 Day-2 correction).

    Non-finite multiplier values are ignored here (the self-check catches them);
    an empty / all-zero set yields ``1.0`` (so the relative residual reduces to the
    absolute one).
    """
    finite = [abs(v) for v in multiplier_values if math.isfinite(v)]
    return max([1.0, *finite]) if finite else 1.0


def relative_residual(raw: float, scale: float) -> float:
    """Relative stationarity residual ``|raw| / scale`` (``scale ≥ 1``). Preserves
    non-finite ``raw`` (``inf``/``nan``) so the fail-closed guard still sees it."""
    if not math.isfinite(raw):
        return raw
    return abs(raw) / scale


@dataclass
class TransferCheck:
    """Outcome of the §2 dual-transfer self-check (fail-closed, conservative)."""

    consistent: bool
    reason: str | None  # why it failed (None when consistent)
    # max relative bound-violation (infeasibility / primal_scale) over comp rows — the guard signal
    max_comp_infeasibility: float
    max_equality_residual: float  # max |val - bound| over equality rows — informational only


def primal_scale(rows: list[RowResidual]) -> float:
    """Magnitude scale for the **relative** complementarity-feasibility check: the
    largest absolute constraint-row *activity* (``comp_*`` + equality rows), floored
    at 1.0. A bound's magnitude (e.g. ``vt ≈ 39136``) sets the scale, so a
    magnitude-50000 variable's NLP-tolerance bound violation is not mistaken for a
    gross breach."""
    mags = [abs(r.val) for r in rows if r.kind != "stationarity" and math.isfinite(r.val)]
    return max([1.0, *mags]) if mags else 1.0


def check_dual_transfer(
    rows: list[RowResidual], feas_tol: float = FEAS_TOL_DEFAULT
) -> TransferCheck:
    """The §2 self-check (design §2 Day-2 correction): fail **closed** and
    **conservative**, so a bad transfer never masquerades as a Case-b emit bug,
    but a healthy model is not falsely blocked.

    Flags ``dual_transfer_inconsistent`` only on:
      (a) a **non-finite** residual on *any* row (NaN/inf — e.g. korcge #1439), or
      (b) a **gross complementarity infeasibility**: a ``comp_*`` (``=g=``) row whose
          *relative* breach ``infeasibility / primal_scale`` exceeds ``feas_tol``.

    Feasibility is the activity ``val`` vs the equation bounds ``[lower, upper]``
    (the constant lives in the bound), so an inactive ``=g=`` row (activity inside
    its bounds) has zero breach, and the breach is **relative** — an absolute floor
    mis-flags an NLP-tolerance bound violation on a large-magnitude variable. Equality
    residuals (``|val - bound|``) are reported (informational) but do **not** block.
    """
    for r in rows:
        # Fail closed on a NaN/Inf activity OR a NaN bound (corrupted gdxdump, e.g.
        # NA/UNDF). A ±Inf *bound* is legitimate (a one-sided =g=/=l= constraint), so
        # only NaN bounds are corruption — `infeasibility` would otherwise treat a
        # non-finite bound as "no bound" and silently ignore it.
        if not math.isfinite(r.val) or math.isnan(r.lower) or math.isnan(r.upper):
            return TransferCheck(False, f"non_finite_residual:{r.label}", math.inf, math.inf)

    scale = primal_scale(rows)
    comp_rows = [r for r in rows if r.kind == "complementarity"]
    eq_resid = [abs(r.signed_residual) for r in rows if r.kind == "equality"]
    rel_infeas = [r.infeasibility / scale for r in comp_rows]
    max_comp = max(rel_infeas) if rel_infeas else 0.0
    max_eq = max(eq_resid) if eq_resid else 0.0

    if max_comp > feas_tol:
        worst = max(comp_rows, key=lambda r: r.infeasibility)
        return TransferCheck(False, f"gross_infeasibility:{worst.label}", max_comp, max_eq)
    return TransferCheck(True, None, max_comp, max_eq)


# Verdict codes and their human labels (design §3).
VERDICT_LABELS = {
    "case_a": "healthy (KKT correct, PATH converges)",
    "case_b": "emit_bug",
    "case_c": "non_convexity (warm-start, not an emit fix)",
    "case_a_or_c": "healthy_residual (cold-start skipped — a-vs-c unresolved)",
    "dual_transfer_inconsistent": "dual_transfer_inconsistent (fix the transfer, re-run)",
}


@dataclass
class Verdict:
    """The Case-(a/b/c) verdict over the stationarity rows (design §3)."""

    code: str
    max_rel: float  # largest relative stationarity residual
    max_row: RowResidual | None  # the prime-suspect row (PR24 trace surface)
    scale: float  # the dual_scale used for the relative residual
    reason: str | None = None  # transfer-inconsistency reason, if any

    @property
    def label(self) -> str:
        return VERDICT_LABELS.get(self.code, self.code)


def classify_verdict(
    stat_rows: list[RowResidual],
    scale: float,
    transfer: TransferCheck,
    tol: float = REL_TOL_DEFAULT,
    cold_start_status: str | None = None,
) -> Verdict:
    """Apply the §3 verdict over the **stationarity** rows after the §2 self-check.

    ``cold_start_status`` is ``"optimal"`` (cold PATH reached the NLP optimum →
    splits Case a from c), ``"diverged"`` (did not), or ``None`` (skipped via
    ``--no-cold-start`` → the a-vs-c split is left unresolved as ``case_a_or_c``).
    The max-residual row is the prime-suspect emit surface (PR24).
    """
    if not transfer.consistent:
        return Verdict("dual_transfer_inconsistent", math.nan, None, scale, transfer.reason)

    best: RowResidual | None = None
    best_rel = 0.0
    for r in stat_rows:
        rel = relative_residual(r.infeasibility, scale)
        if not math.isfinite(rel):  # fail closed (the self-check should have caught it)
            return Verdict(
                "dual_transfer_inconsistent", rel, r, scale, f"non_finite_residual:{r.label}"
            )
        if rel > best_rel:
            best_rel, best = rel, r

    if best_rel > tol:
        return Verdict("case_b", best_rel, best, scale)
    if cold_start_status == "optimal":
        return Verdict("case_a", best_rel, best, scale)
    if cold_start_status == "diverged":
        return Verdict("case_c", best_rel, best, scale)
    # None (--no-cold-start) or "unavailable" — the a-vs-c split is unresolved.
    return Verdict("case_a_or_c", best_rel, best, scale)


def build_report(
    model: str,
    tol: float,
    verdict: Verdict,
    transfer: TransferCheck,
    stat_rows: list[RowResidual],
    top_n: int = 5,
) -> dict[str, object]:
    """Assemble the JSON-serializable report (design §4) — the single source both
    :func:`format_json` and :func:`format_human` render."""

    def row_dict(r: RowResidual) -> dict[str, object]:
        return {
            "name": r.name,
            "index": list(r.index),
            "residual": r.signed_residual,
            "relative": relative_residual(r.infeasibility, verdict.scale),
            "kind": r.kind,
        }

    def rank_key(r: RowResidual) -> float:
        rel = relative_residual(r.infeasibility, verdict.scale)
        return rel if math.isfinite(rel) else math.inf

    ranked = sorted(stat_rows, key=rank_key, reverse=True)
    return {
        "model": model,
        "tol": tol,
        "dual_scale": verdict.scale,
        "dual_transfer": {
            "consistent": transfer.consistent,
            "reason": transfer.reason,
            "max_comp_infeasibility": transfer.max_comp_infeasibility,
            "max_equality_residual": transfer.max_equality_residual,
        },
        "verdict": verdict.code,
        "verdict_label": verdict.label,
        "max_residual_row": row_dict(verdict.max_row) if verdict.max_row else None,
        "rows": [row_dict(r) for r in ranked[:top_n]],
    }


def _json_sanitize(obj: object) -> object:
    """Recursively replace non-finite floats (``NaN``/``±Inf``) with ``None`` so the
    ``--json`` report is valid JSON for strict consumers (the harness emits non-finite
    residuals for div-by-zero rows, cf. korcge #1439)."""
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _json_sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_sanitize(v) for v in obj]
    return obj


def format_json(report: dict[str, object]) -> str:
    """Render the report as strict, indented JSON (design §4) — non-finite floats are
    sanitized to ``null`` so the machine-readable evidence is always valid JSON."""
    return json.dumps(_json_sanitize(report), indent=2, allow_nan=False)


def format_human(report: dict[str, object]) -> str:
    """Render the human stdout summary (design §4)."""
    transfer = report["dual_transfer"]
    assert isinstance(transfer, dict)
    if transfer["consistent"]:
        xfer = f"CONSISTENT (max comp infeas {transfer['max_comp_infeasibility']:.2e} rel"
        xfer += f", max equality residual {transfer['max_equality_residual']:.2e} raw)"
    else:
        xfer = f"INCONSISTENT ({transfer['reason']})"

    lines = [
        f"model: {report['model']}    tol: {report['tol']:g} (relative)",
        f"dual scale: {report['dual_scale']:.3g}",
        f"dual transfer: {xfer}",
        f"verdict: {str(report['verdict']).upper()}  — {report['verdict_label']}",
    ]
    mr = report["max_residual_row"]
    if isinstance(mr, dict):
        lines.append(
            f"max-residual row: {_row_label(mr)}   "
            f"rel = {float(mr['relative']):.2e}  (raw {float(mr['residual']):.2e})"
        )
    rows = report["rows"]
    if isinstance(rows, list) and rows:
        lines.append("top stationarity rows:")
        for r in rows:
            assert isinstance(r, dict)
            lines.append(f"  {_row_label(r):<24} rel {float(r['relative']):.2e}")
    return "\n".join(lines)


def _row_label(row_dict: dict[str, object]) -> str:
    name = str(row_dict["name"])
    index = row_dict["index"]
    if isinstance(index, list) and index:
        return f"{name}({','.join(str(i) for i in index)})"
    return name


def emit_warmstarted_mcp(model_path: Path, out_path: Path) -> dict[str, object]:
    """Emit the MCP with ``--nlp-presolve`` (primal + dual warm-start) via the
    production emit path — Architecture A reuse. Returns the translate result
    dict (``status``/``output_file``/``error``).
    """
    from scripts.gamslib.batch_translate import translate_single_model

    return translate_single_model(model_path, out_path, nlp_presolve=True)


# --- MCP-text parsing for the GAMS run -------------------------------------

_EQUATIONS_BLOCK_RE = re.compile(r"^\s*Equations\b(.*?)^\s*;", re.MULTILINE | re.DOTALL)
_EQ_NAME_RE = re.compile(r"^\s*([A-Za-z]\w*)\s*(?:\([^)]*\))?\s*$", re.MULTILINE)


def extract_equation_names(mcp_text: str) -> list[str]:
    """Parse the declared equation symbols from the MCP's ``Equations … ;`` block(s)
    — the symbols the harness reads back from the residual GDX. Order-preserving,
    de-duplicated."""
    names: list[str] = []
    seen: set[str] = set()
    for block in _EQUATIONS_BLOCK_RE.findall(mcp_text):
        for name in _EQ_NAME_RE.findall(block):
            if name not in seen:
                seen.add(name)
                names.append(name)
    return names


def extract_multiplier_names(mcp_text: str) -> list[str]:
    """The multiplier symbols (``nu_*``/``lam_*``/``piL_*``/``piU_*``) the warm-start
    transfers — the set ``dual_scale`` is taken over (design §3). Order-preserving."""
    names: list[str] = []
    seen: set[str] = set()
    for line in mcp_text.splitlines():
        m = _MULT_RE.match(line.strip())
        if m is None:
            continue
        sym = line.strip().split(".l", 1)[0].strip()
        if sym and sym not in seen:
            seen.add(sym)
            names.append(sym)
    return names


# --- --gdx skip variant (design §1 / §8) -----------------------------------

_NLP_SOLVE_RE = re.compile(
    r"^([ \t]*)(Solve\s+\w+\s+using\s+(?:NLP|DNLP|QCP)\b[^;]*;)",
    re.IGNORECASE | re.MULTILINE,
)


def neutralize_nlp_solve(source_text: str) -> tuple[str, int]:
    """Comment out the embedded NLP ``Solve`` statement(s) in a source model so the
    ``--gdx`` path can substitute a pre-solved solution (``execute_loadpoint``)
    instead of re-solving (design §8). Returns ``(new_text, n_neutralized)``."""

    def comment(match: re.Match[str]) -> str:
        return f"{match.group(1)}* [kkt-residual --gdx] NLP solve skipped: {match.group(2)}"

    return _NLP_SOLVE_RE.subn(comment, source_text)


def build_gdx_skip_variant(
    mcp_text: str, source_basename: str, neutralized_include: str, gdx_path: str
) -> str:
    """Rewrite the presolve MCP so the embedded NLP solve is skipped and primals +
    marginals load from ``gdx_path`` instead (design §1 ``--gdx`` path).

    Repoints the ``$include`` of the source (matched by basename) at the neutralized
    copy and injects ``execute_loadpoint`` right after it. Raises ``ValueError`` if
    the source ``$include`` is not found.
    """
    include_re = re.compile(
        rf'^([ \t]*)\$include\s+"[^"]*{re.escape(source_basename)}"\s*$',
        re.MULTILINE,
    )

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1)
        return (
            f'{indent}$include "{neutralized_include}"\n' f"{indent}execute_loadpoint '{gdx_path}';"
        )

    new_text, n = include_re.subn(repl, mcp_text)
    if n == 0:
        raise ValueError(
            f"no `$include` of the source model ({source_basename}) found to rewrite "
            "for the --gdx load-point path"
        )
    if n > 1:
        raise ValueError(
            f"expected exactly one `$include` of the source model ({source_basename}), "
            f"found {n} — refusing to inject multiple `execute_loadpoint` statements"
        )
    return new_text


# --- GAMS execution + gdxdump ----------------------------------------------

_GAMS_CANDIDATES = (
    "/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams",
    "/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams",
    "/opt/gams/gams",
    "C:\\GAMS\\win64\\gams.exe",
)


def find_gams_tools() -> tuple[str, str] | None:
    """Locate the ``gams`` and (sibling) ``gdxdump`` executables, mirroring
    ``scripts/gamslib/test_solve.py``. Returns ``(gams, gdxdump)`` or ``None`` if
    GAMS is unavailable (the GAMS-run paths then no-op / skip). Checks both the
    bare and ``.exe`` sibling names so it works on Windows (``gdxdump.exe`` next to
    ``gams.exe``) as well as POSIX."""
    gams = next((p for p in _GAMS_CANDIDATES if Path(p).exists()), None) or shutil.which("gams")
    if not gams:
        return None
    sibling = next(
        (
            str(s)
            for name in ("gdxdump", "gdxdump.exe")
            if (s := Path(gams).with_name(name)).exists()
        ),
        None,
    )
    gdxdump = sibling or shutil.which("gdxdump")
    if not gdxdump:
        return None
    return gams, gdxdump


def run_gams(gms_path: Path, scratch: Path, gams_exe: str, timeout: int = 120) -> Path:
    """Run GAMS on ``gms_path`` from ``PROJECT_ROOT`` (so the repo-relative
    ``$include`` resolves, cf. test_solve #1275). Scratch/listing land in
    ``scratch``. Returns the ``.lst`` path.

    Raises ``RuntimeError`` on a non-zero GAMS exit (a compile/execution error —
    e.g. the korcge #1439 presolve abort) with the stderr/listing tail so the
    failure is actionable, or on a missing listing. A normal ``iterlim=0`` run
    returns 0 (the MCP solve interrupts at iteration 0 but executes cleanly), so
    this does not false-positive on the residual-only evaluation."""
    lst_path = scratch / f"{gms_path.stem}.lst"
    proc = subprocess.run(
        [
            gams_exe,
            str(gms_path),
            f"o={lst_path}",
            "lo=2",
            f"reslim={timeout}",
            f"ScrDir={scratch}",
        ],
        capture_output=True,
        text=True,
        timeout=timeout + 30,
        cwd=str(PROJECT_ROOT),
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[-1500:]
        lst_errors = ""
        if lst_path.exists():
            lst_errors = "\n".join(
                ln
                for ln in lst_path.read_text(errors="replace").splitlines()
                if ln.startswith("****")
            )[-1500:]
        raise RuntimeError(
            f"GAMS exited {proc.returncode} on {gms_path.name}"
            + (f"\nstderr/stdout: {detail}" if detail else "")
            + (f"\nlisting errors:\n{lst_errors}" if lst_errors else "")
        )
    if not lst_path.exists():
        raise RuntimeError(f"GAMS produced no listing for {gms_path}")
    return lst_path


def gdxdump_symbol(gdx_path: Path, symbol: str, gdxdump_exe: str) -> dict[tuple[str, ...], float]:
    """Dump one symbol's ``Val`` field from a GDX as CSV (``{index: value}``) — used
    for multiplier *variables* (``dual_scale``). Absent/empty symbol → ``{}``."""
    proc = subprocess.run(
        [gdxdump_exe, str(gdx_path), f"symb={symbol}", "format=csv"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        return {}
    return parse_gdxdump_csv(proc.stdout)


def gdxdump_equation(
    gdx_path: Path, symbol: str, gdxdump_exe: str
) -> dict[tuple[str, ...], tuple[float, float, float]]:
    """Dump one equation symbol's ``Val``/``Lower``/``Upper`` fields (CSVAllFields) —
    needed because a constraint's constant lives in the bound, not ``Val``."""
    proc = subprocess.run(
        [gdxdump_exe, str(gdx_path), f"symb={symbol}", "format=csv", "CSVAllFields"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        return {}
    return parse_gdxdump_allfields(proc.stdout)


def collect_residuals(
    gdx_path: Path, equation_names: list[str], gdxdump_exe: str
) -> list[RowResidual]:
    """Read every equation's per-record ``Val``/``Lower``/``Upper`` (the residual at
    the warm-start is the activity vs its bounds) into a flat list."""
    rows: list[RowResidual] = []
    for name in equation_names:
        for index, (val, lower, upper) in gdxdump_equation(gdx_path, name, gdxdump_exe).items():
            rows.append(RowResidual.from_fields(name, index, val, lower, upper))
    return rows


def collect_multiplier_values(
    gdx_path: Path, multiplier_names: list[str], gdxdump_exe: str
) -> list[float]:
    """Read every transferred multiplier's level from the GDX (for ``dual_scale``)."""
    values: list[float] = []
    for name in multiplier_names:
        values.extend(gdxdump_symbol(gdx_path, name, gdxdump_exe).values())
    return values


def cold_start_status(model_path: Path, scratch: Path, timeout: int = 120) -> str:
    """Cold-start MCP solve (design §3, Case-a-vs-c split): emit the *non-presolve*
    MCP and solve it from the default start. (Uses ``solve_mcp``, which performs its
    own GAMS discovery — no ``gams_exe`` argument needed.)

    Returns ``"optimal"`` if PATH reaches a (locally) optimal model status (1/2),
    ``"diverged"`` if it reaches an infeasible / non-converged status, or
    ``"unavailable"`` if the cold MCP could not be produced (so the a-vs-c split is
    left unresolved rather than mislabelled Case c). The translate ``status`` can be
    ``"failure"`` from a post-emit compile check even when a solvable file is
    written, so the file's existence — not that flag — gates the solve."""
    from scripts.gamslib.batch_translate import translate_single_model
    from scripts.gamslib.test_solve import solve_mcp

    cold_path = scratch / f"{model_path.stem}_mcp_cold.gms"
    translate_single_model(model_path, cold_path, nlp_presolve=False)
    if not cold_path.exists():
        return "unavailable"
    solved = solve_mcp(cold_path, timeout=timeout)
    if solved.get("model_status") in (1, 2):
        return "optimal"
    if solved.get("model_status") is None:
        return "unavailable"  # GAMS couldn't run / no status parsed
    return "diverged"


def build_residual_only_mcp(
    mcp_text: str,
    residual_gdx: str,
    *,
    gdx: str | None,
    source_basename: str | None,
    neutralized_include: str | None,
) -> str:
    """Compose the residual-only MCP from the warm-started presolve emit:
    (optionally) wire the ``--gdx`` load-point — repointing the ``$include`` of
    ``source_basename`` at ``neutralized_include`` — apply the ``nu`` sign
    correction, insert ``iterlim=0``, and append ``execute_unload`` of the
    residual GDX."""
    text = mcp_text
    if gdx is not None:
        if neutralized_include is None or source_basename is None:
            raise ValueError(
                "build_residual_only_mcp: gdx set but source_basename/neutralized_include "
                "missing (both are required to wire the --gdx load-point)"
            )
        text = build_gdx_skip_variant(text, source_basename, neutralized_include, gdx)
    text = apply_residual_sign_correction(text)
    text = make_residual_only(text)
    return inject_residual_unload(text, residual_gdx)


def run_harness(
    model_path: Path,
    scratch: Path,
    *,
    tol: float,
    gdx: str | None,
    no_cold_start: bool,
    gams_tools: tuple[str, str],
    timeout: int = 120,
) -> dict[str, object]:
    """End-to-end Architecture-A residual evaluation → report (design §1–§4).

    Emits the warm-started MCP, builds the residual-only variant, runs it at
    ``iterlim=0``, reads per-row residuals from the GDX, runs the §2 self-check and
    the §3 verdict (optional cold-start for the a-vs-c split), and returns the
    report dict. Raises on emit / GAMS failure.
    """
    gams_exe, gdxdump_exe = gams_tools

    presolve_path = scratch / f"{model_path.stem}_mcp_presolve.gms"
    emit = emit_warmstarted_mcp(model_path, presolve_path)
    if emit.get("status") != "success":
        raise RuntimeError(f"warm-started MCP emit failed: {emit.get('error')}")
    mcp_text = presolve_path.read_text(encoding="utf-8")

    equation_names = extract_equation_names(mcp_text)
    multiplier_names = extract_multiplier_names(mcp_text)

    neutralized_include: str | None = None
    if gdx is not None:
        neutralized = scratch / f"{model_path.stem}_nlp_neutralized.gms"
        new_src, n = neutralize_nlp_solve(model_path.read_text(encoding="utf-8"))
        neutralized.write_text(new_src, encoding="utf-8")
        neutralized_include = neutralized.as_posix()
        if n == 0:
            print(
                "[kkt-residual] WARNING: --gdx given but no NLP Solve found to neutralize "
                f"in {model_path.name}; the load-point will run after the embedded solve.",
                file=sys.stderr,
            )

    residual_gdx = (scratch / "kkt_residuals.gdx").as_posix()
    gdx_abs = str(Path(gdx).resolve()) if gdx is not None else None
    residual_text = build_residual_only_mcp(
        mcp_text,
        residual_gdx,
        gdx=gdx_abs,
        source_basename=model_path.name if gdx is not None else None,
        neutralized_include=neutralized_include,
    )
    residual_path = scratch / f"{model_path.stem}_mcp_presolve_residual.gms"
    residual_path.write_text(residual_text, encoding="utf-8")

    print(f"[kkt-residual] {model_path.name} — running residual eval (iterlim=0)…")
    run_gams(residual_path, scratch, gams_exe, timeout=timeout)

    rows = collect_residuals(Path(residual_gdx), equation_names, gdxdump_exe)
    if not rows:
        raise RuntimeError(
            "no equation residuals read from the GDX — the iterlim=0 solve may have "
            "failed to execute (check the listing)"
        )
    mult_values = collect_multiplier_values(Path(residual_gdx), multiplier_names, gdxdump_exe)
    scale = dual_scale(mult_values)
    stat_rows = [r for r in rows if r.kind == "stationarity"]

    transfer = check_dual_transfer(rows)
    cold = None
    if transfer.consistent and not no_cold_start:
        print("[kkt-residual] cold-start MCP solve (Case a-vs-c split)…")
        cold = cold_start_status(model_path, scratch, timeout=timeout)

    verdict = classify_verdict(stat_rows, scale, transfer, tol=tol, cold_start_status=cold)
    return build_report(model_path.stem, tol, verdict, transfer, stat_rows)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kkt_residual.py",
        description=(
            "KKT-residual verification harness (Sprint 28 Priority 9 / PR27): "
            "warm-start the MCP from the NLP KKT point and evaluate per-row "
            "residuals to classify Case (a) healthy / (b) emit bug / (c) "
            "non-convexity."
        ),
    )
    parser.add_argument("model", help="source NLP model (.gms) the pipeline translates")
    parser.add_argument(
        "--gdx",
        metavar="SOLUTION.gdx",
        help=(
            "pre-solved NLP solution (primals + marginals); skips the embedded NLP "
            "solve via execute_loadpoint (for slow NLPs, design §8)"
        ),
    )
    parser.add_argument(
        "--tol",
        type=float,
        default=None,
        help=(
            f"relative stationarity-residual tolerance |F|/dual_scale for the verdict "
            f"(default {REL_TOL_DEFAULT})"
        ),
    )
    parser.add_argument(
        "--json",
        metavar="OUT.json",
        help="write the machine-readable report here (human summary always goes to stdout)",
    )
    parser.add_argument(
        "--nlp-solver",
        default=None,
        help=(
            "NLP solver override for the path that solves the NLP when --gdx is "
            f"omitted (will default to {DEFAULT_NLP_SOLVER} once implemented; not honored "
            "in the Day-2 build — the embedded --nlp-presolve solve uses the model/GAMS "
            "default)"
        ),
    )
    parser.add_argument(
        "--no-cold-start",
        action="store_true",
        help=(
            "skip the cold-start MCP solve that splits Case a from Case c; report the "
            "residual + Case b/guard only (verdict case_a_or_c when residual is clean)"
        ),
    )
    parser.add_argument(
        "--keep-files",
        action="store_true",
        help="keep the generated scratch MCP files (default: delete the scratch dir on exit)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    # --nlp-solver is the one still-deferred flag (the embedded --nlp-presolve solve
    # uses the model/GAMS default under Architecture A) — fail fast rather than
    # silently ignore it.
    if args.nlp_solver is not None:
        print(
            "error: --nlp-solver is not honored in the Day-2 build (the embedded "
            "--nlp-presolve solve uses the model/GAMS default); omit it.",
            file=sys.stderr,
        )
        return 2

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"error: model not found: {model_path}", file=sys.stderr)
        return 2
    if args.gdx is not None and not Path(args.gdx).exists():
        print(f"error: --gdx solution not found: {args.gdx}", file=sys.stderr)
        return 2

    gams_tools = find_gams_tools()
    if gams_tools is None:
        print(
            "error: GAMS (and gdxdump) not found — the residual evaluation needs a "
            "GAMS install. See scripts/gamslib/test_solve.py for the search paths.",
            file=sys.stderr,
        )
        return 3

    tol = args.tol if args.tol is not None else REL_TOL_DEFAULT

    # Scratch under PROJECT_ROOT/output (gitignored) — never the committed golden dir,
    # and never outside the repo: translate_single_model reports paths relative to
    # PROJECT_ROOT. Deleted on exit unless --keep-files (cf. check_convexity.py).
    scratch_root = PROJECT_ROOT / "output"
    scratch_root.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f"kkt_residual_{model_path.stem}_", dir=scratch_root))
    failed = False
    try:
        report = run_harness(
            model_path,
            scratch,
            tol=tol,
            gdx=args.gdx,
            no_cold_start=args.no_cold_start,
            gams_tools=gams_tools,
        )
    except subprocess.TimeoutExpired as exc:
        failed = True
        print(f"error: GAMS timed out: {exc}", file=sys.stderr)
        return 1
    except (RuntimeError, ValueError) as exc:
        failed = True
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        # Retain scratch (the .gms + .lst) on failure so "check the listing" is
        # actionable, or whenever --keep-files is set; delete on clean success.
        if args.keep_files or failed:
            if scratch.exists():
                print(f"[kkt-residual] scratch retained: {scratch}", file=sys.stderr)
        else:
            shutil.rmtree(scratch, ignore_errors=True)

    print(format_human(report))
    if args.json:
        try:
            Path(args.json).write_text(format_json(report) + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"error: could not write JSON report to {args.json}: {exc}", file=sys.stderr)
            return 1
        print(f"[kkt-residual] JSON report written: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
