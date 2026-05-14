#!/usr/bin/env python3
"""Parse ``.github/path-solve-ci-targets.txt`` into JSON for PR19 CI.

Output schema::

    {
      "tier_0_1": [{"model": "dispatch", "tier": "0", "reslim": null}, ...],
      "pattern_c": [{"model": "camcge",   "tier": "pattern-c", "reslim": null}, ...]
    }

Per `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` §"Target Model List":
- Blank lines + lines starting with `#` are ignored.
- One model per line; optional inline `# tier=<0|1|pattern-c>` and `reslim=<N>` annotations.
- tier=0 / tier=1 → hard-fail bucket (``tier_0_1``).
- tier=pattern-c → soft-fail bucket (``pattern_c``).
- Models without an explicit tier annotation default to tier=1 (hard-fail) — matches
  the design doc's "tier=1" line in the example block.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ANNOTATION = re.compile(r"\b(?P<key>tier|reslim)\s*=\s*(?P<value>[a-zA-Z0-9_-]+)")


class TargetParseError(ValueError):
    """Raised on malformed target-list entries.

    Surfaced via main() as a non-zero exit so CI fails loudly when the
    target list has a typo (e.g., ``tier=patternc`` silently dropping a
    model from coverage, or ``reslim=30s`` crashing without a useful
    line reference).
    """


def parse_targets(path: Path) -> dict:
    tier_0_1: list[dict] = []
    pattern_c: list[dict] = []
    for line_no, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        comment_idx = line.find("#")
        model_part = (line if comment_idx < 0 else line[:comment_idx]).strip()
        annotation_part = "" if comment_idx < 0 else line[comment_idx:]
        if not model_part:
            continue
        annotations = {
            m.group("key"): m.group("value") for m in _ANNOTATION.finditer(annotation_part)
        }
        tier = annotations.get("tier", "1")
        reslim_raw = annotations.get("reslim")
        if reslim_raw is None:
            reslim: int | None = None
        else:
            try:
                reslim = int(reslim_raw)
            except ValueError as exc:
                raise TargetParseError(
                    f"line {line_no}: malformed reslim={reslim_raw!r} "
                    f"(must be an integer number of seconds): {raw_line!r}"
                ) from exc
            if reslim < 0:
                raise TargetParseError(
                    f"line {line_no}: invalid reslim={reslim} "
                    f"(must be >= 0 seconds): {raw_line!r}"
                )
        entry = {"model": model_part, "tier": tier, "reslim": reslim}
        if tier == "pattern-c":
            pattern_c.append(entry)
        elif tier in ("0", "1"):
            tier_0_1.append(entry)
        else:
            raise TargetParseError(
                f"line {line_no}: unknown tier {tier!r} "
                f"(expected one of 0, 1, pattern-c): {raw_line!r}"
            )
    return {"tier_0_1": tier_0_1, "pattern_c": pattern_c}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: parse_pr19_targets.py <path-to-targets.txt>", file=sys.stderr)
        return 2
    targets_path = Path(sys.argv[1])
    if not targets_path.is_file():
        print(f"error: target list not found: {targets_path}", file=sys.stderr)
        return 2
    try:
        targets = parse_targets(targets_path)
    except TargetParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(targets, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
