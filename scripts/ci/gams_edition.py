#!/usr/bin/env python3
"""Print the GAMS edition (``edition=demo|licensed|unknown``) and nothing else.

Sprint 40 P1 (``CI_LICENSE_DESIGN.md`` §3, §6). It replaces every raw
``gams audit lo=2`` print in CI. A CI log is published, and raw audit or listing
output can carry the licensee, license ID, license path and node fields.

The control is ORDERING, not scanning: GAMS runs a tiny probe with ALL of its
output (stdout, stderr, log, listing, process dir) captured inside a temp dir.
The listing is classified there by the shared parser
(``scripts.gamslib.test_solve.extract_license_edition``, one parser for every
stage), and only the verdict, plus the generic version number, is printed. No
GAMS output is ever echoed, including on failure.

Usage:
    python3 scripts/ci/gams_edition.py [--gams PATH] [--require demo|licensed]

Exit codes: 0 = classified (and matches ``--require``, if given);
1 = classified but does not match ``--require``; 2 = could not classify.

Stdlib-only, so it runs in workflows that never ``pip install`` (PR19).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.test_solve import (  # noqa: E402
    extract_gams_version,
    extract_license_edition,
)

#: Tiny NLP: well under the demo ceiling, so both editions solve it. The edition
#: is read from the listing's own markers, not inferred from whether it solved.
PROBE = (
    "variable x, z; equation e; e.. z =e= sqr(x - 1);\n"
    "model m /all/; solve m using nlp minimizing z;\n"
)


def classify(gams: str, timeout: int = 120) -> tuple[str | None, str | None]:
    """Run the probe; return ``(edition, gams_version)`` from its own listing.

    Every byte GAMS writes lands in a temp dir that is deleted on return.
    ``procDirPath`` keeps the process dir (which holds a license copy) there too.
    """
    with (
        tempfile.TemporaryDirectory(prefix="gams_edition_") as work,
        tempfile.TemporaryDirectory(prefix="gams_procdir_") as procdir,
    ):
        probe = Path(work) / "probe.gms"
        probe.write_text(PROBE)
        lst = Path(work) / "probe.lst"
        try:
            subprocess.run(
                [gams, str(probe), f"o={lst}", "lo=0", f"procDirPath={procdir}"],
                cwd=work,
                capture_output=True,  # captured and DISCARDED: never printed
                text=True,
                timeout=timeout,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return None, None
        if not lst.is_file():
            return None, None
        text = lst.read_text(errors="replace")
        return extract_license_edition(text), extract_gams_version(text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--gams", default="gams", help="GAMS executable (default: gams on PATH)")
    ap.add_argument("--require", choices=["demo", "licensed"], default=None)
    args = ap.parse_args(argv)

    edition, version = classify(args.gams)
    print(f"edition={edition or 'unknown'}")
    if version:
        print(f"gams_version={version}")
    if edition is None:
        print("::error::could not classify the GAMS edition (no probe listing)")
        return 2
    if args.require and edition != args.require:
        print(f"::error::expected edition={args.require}, got edition={edition}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
