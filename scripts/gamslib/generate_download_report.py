#!/usr/bin/env python3
"""Generate download report for GAMSLIB models."""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
CATALOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "catalog.json"
REPORT_PATH = PROJECT_ROOT / "data" / "gamslib" / "download_report.md"


def generate_report() -> None:
    """Generate the download report."""
    # Load catalog
    with open(CATALOG_PATH) as f:
        data = json.load(f)

    # Gather statistics
    models = data["models"]
    downloaded = [m for m in models if m["download_status"] == "downloaded"]
    pending = [m for m in models if m["download_status"] == "pending"]
    failed = [m for m in models if m["download_status"] == "failed"]

    # Count by type
    by_type: dict[str, int] = {}
    for m in downloaded:
        t = m["gamslib_type"]
        by_type[t] = by_type.get(t, 0) + 1

    # Calculate total size
    total_bytes = sum(m.get("file_size_bytes", 0) for m in downloaded)

    # Find largest and smallest
    sorted_by_size = sorted(downloaded, key=lambda m: m.get("file_size_bytes", 0), reverse=True)
    largest = sorted_by_size[:5]
    smallest = sorted_by_size[-5:]

    report = f"""# GAMSLIB Download Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Summary

| Metric | Count |
|--------|-------|
| Total models in catalog | {len(models)} |
| Successfully downloaded | {len(downloaded)} |
| Pending | {len(pending)} |
| Failed | {len(failed)} |

## Download Statistics

| Statistic | Value |
|-----------|-------|
| Total bytes downloaded | {total_bytes:,} |
| Total size (MB) | {total_bytes / 1024 / 1024:.2f} |
| Average file size | {total_bytes // len(downloaded) if downloaded else 0:,} bytes |

## Downloads by Model Type

| Type | Count |
|------|-------|
| LP | {by_type.get("LP", 0)} |
| NLP | {by_type.get("NLP", 0)} |
| QCP | {by_type.get("QCP", 0)} |
| **Total** | **{len(downloaded)}** |

## Largest Models

| Model | Type | Size (bytes) |
|-------|------|--------------|
"""

    for m in largest:
        report += f"| {m['model_id']} | {m['gamslib_type']} | {m.get('file_size_bytes', 0):,} |\n"

    report += """
## Smallest Models

| Model | Type | Size (bytes) |
|-------|------|--------------|
"""

    for m in smallest:
        report += f"| {m['model_id']} | {m['gamslib_type']} | {m.get('file_size_bytes', 0):,} |\n"

    if failed:
        report += """
## Failed Downloads

| Model | Error |
|-------|-------|
"""
        for m in failed:
            report += f"| {m['model_id']} | {m.get('notes', 'Unknown')} |\n"
    else:
        report += """
## Failed Downloads

None - all downloads successful!
"""

    report += """
---

## Notes

- All models downloaded using the `gamslib` command-line tool
- Files stored in `data/gamslib/raw/` (gitignored)
- Catalog updated with file sizes and download timestamps
- LP models are verified convex by definition
- NLP and QCP models require convexity verification (Sprint 13 Days 5-6)
"""

    with open(REPORT_PATH, "w") as f:
        f.write(report)

    print(f"Download report created: {REPORT_PATH}")


if __name__ == "__main__":
    generate_report()
