# GAMSLIB Dashboard Design

**Date:** 2025-11-12  
**Unknown:** 3.4 (Medium Priority)  
**Owner:** Validation Team  
**Status:** ✅ RESOLVED

---

## Assumption

Sprint 6 needs a dashboard to visualize GAMSLIB benchmark results, showing KPIs, model status, and error breakdowns in an easy-to-read format.

---

## Research Questions

1. What format should the dashboard use: Markdown, HTML, or interactive web app?
2. What information should be displayed: KPIs, model table, error breakdown?
3. Should the dashboard be static (file) or dynamic (web server)?
4. How should we visualize the cascade (parse → convert → solve)?
5. What level of detail: summary only, or drill-down to individual errors?

---

## Investigation

### Dashboard Requirements

Based on Sprint 6 goals and Unknown 3.4:

**Must Have:**
1. Display 4 primary KPIs (parse%, convert%, solve%, e2e%)
2. Show target achievement (conservative, stretch)
3. List all models with their status at each stage
4. Breakdown of parse errors by category (from Unknown 3.3)
5. Generated from benchmark run data (JSON input)

**Nice to Have:**
1. Visual indicators (✅/❌ icons, colored bars)
2. Timestamp and metadata (when run, tool version)
3. Links to error documentation (from Unknown 4.2)
4. Sortable/filterable model table
5. Comparison across multiple runs

**Out of Scope for Sprint 6:**
- Real-time updates (static file sufficient)
- Interactive charts (too complex for first version)
- Historical trend analysis (need multiple runs first)

---

## Option Analysis

### Option A: Pure Markdown Dashboard ⭐ RECOMMENDED

**Description:** Generate a Markdown file (`GAMSLIB_RESULTS.md`) with text tables and emoji indicators

**Technology:**
- Python script reads JSON results
- Generates Markdown using string templates or Jinja2
- Output: Single `.md` file in repo

**Pros:**
- ✅ Simplest implementation (1-2 hours)
- ✅ GitHub renders Markdown beautifully
- ✅ Version controlled (can track changes over time)
- ✅ No dependencies (pure Python + stdlib)
- ✅ Easy to read in terminal or web
- ✅ Works offline

**Cons:**
- ⚠️ Limited interactivity (no sorting, filtering)
- ⚠️ Static content only
- ⚠️ No charts or visualizations

**Example Output:**
```markdown
# GAMSLIB Benchmark Results

**Generated:** 2025-11-12 14:30:00  
**Tool Version:** nlp2mcp 0.3.0  
**Model Tier:** Tier 1 (10 models)

---

## KPI Summary

| KPI | Value | Target (Conservative) | Target (Stretch) | Status |
|-----|-------|----------------------|------------------|--------|
| Parse Rate | 60.0% (6/10) | ≥ 50% | ≥ 70% | ✅ PASS |
| Convert Rate | 83.3% (5/6) | ≥ 80% | ≥ 90% | ✅ PASS |
| Solve Rate | 60.0% (3/5) | ≥ 50% | ≥ 70% | ✅ PASS |
| E2E Success | 30.0% (3/10) | ≥ 20% | ≥ 45% | ✅ PASS |

**Overall:** ✅ Conservative targets met | ❌ Stretch targets not met

---

## Model Results

| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| trig | ✅ PASS | ✅ PASS | ✅ PASS | ✅ | Solved in 0.12s |
| rbrock | ✅ PASS | ✅ PASS | ✅ PASS | ✅ | Solved in 0.08s |
| mhw4d | ✅ PASS | ✅ PASS | ✅ PASS | ✅ | Solved in 0.15s |
| hs62 | ✅ PASS | ✅ PASS | ❌ FAIL | ❌ | PATH failed: Nonconvex |
| mathopt1 | ✅ PASS | ✅ PASS | ❌ FAIL | ❌ | PATH failed: Unbounded |
| himmel16 | ❌ FAIL | - | - | ❌ | Parse error: INDEXED_OPERATION |
| circle | ❌ FAIL | - | - | ❌ | Parse error: DOLLAR_CONDITION |
| maxmin | ❌ FAIL | - | - | ❌ | Parse error: INDEXED_OPERATION |
| mhw4dx | ❌ FAIL | - | - | ❌ | Parse error: SYNTAX_ERROR |
| mingamma | ✅ PASS | ❌ FAIL | - | ❌ | Convert error: Unsupported function |

---

## Error Breakdown

### Parse Errors (4 models)

| Category | Count | Models |
|----------|-------|--------|
| INDEXED_OPERATION | 2 | himmel16, maxmin |
| DOLLAR_CONDITION | 1 | circle |
| SYNTAX_ERROR | 1 | mhw4dx |

### Convert Errors (1 model)

| Error Type | Count | Models |
|------------|-------|--------|
| Unsupported Function | 1 | mingamma |

### Solve Errors (2 models)

| PATH Status | Count | Models |
|-------------|-------|--------|
| Nonconvex Problem | 1 | hs62 |
| Unbounded | 1 | mathopt1 |

---

## Details

### Parse Failures

**himmel16.gms**
- Category: INDEXED_OPERATION
- Error: Lead operator `i++1` not supported
- Line: 32
- Docs: https://docs.nlp2mcp.dev/errors/#indexed-operation

**circle.gms**
- Category: DOLLAR_CONDITION
- Error: Dollar condition `$(ord(i) < ord(j))` not supported
- Line: 18
- Docs: https://docs.nlp2mcp.dev/errors/#dollar-condition

[... more details ...]
```

**Assessment:** Best for Sprint 6

---

### Option B: HTML Dashboard from Markdown

**Description:** Generate Markdown, then convert to HTML using a tool like `markdown2html` or `pandoc`

**Technology:**
- Generate Markdown (same as Option A)
- Convert to HTML: `pandoc GAMSLIB_RESULTS.md -o GAMSLIB_RESULTS.html`
- Add CSS styling for better visuals

**Pros:**
- ✅ More polished appearance
- ✅ Can embed CSS for colors, fonts
- ✅ Clickable links work better
- ✅ Can add custom styling

**Cons:**
- ⚠️ Requires external tool (pandoc) or library
- ⚠️ Two files to maintain (.md and .html)
- ⚠️ Not as easy to version control (HTML diffs are messy)
- ⚠️ More implementation time (3-4 hours)

**Assessment:** Overkill for Sprint 6, consider for Sprint 7+

---

### Option C: Dynamic Dashboard (Web App)

**Description:** Build a small Flask/FastAPI web server that displays benchmark results interactively

**Technology:**
- Backend: Flask or FastAPI
- Frontend: HTML + JavaScript (maybe React)
- Data: Read JSON results from disk
- Features: Sorting, filtering, charts

**Pros:**
- ✅ Full interactivity (sort, filter, search)
- ✅ Can add charts (Chart.js, Plotly)
- ✅ Compare multiple benchmark runs
- ✅ Better UX for exploring results

**Cons:**
- ❌ Significantly more complex (8-16 hours)
- ❌ Requires web server to run
- ❌ More dependencies (Flask, frontend libs)
- ❌ Overkill for 10 models
- ❌ Hard to version control (dynamic content)

**Assessment:** Too complex for Sprint 6, consider for Sprint 8+ if needed

---

### Option D: Terminal-Only Output (No Dashboard)

**Description:** Just print results to console, no persistent dashboard file

**Technology:**
- Python script prints formatted output
- Use `rich` library for colored tables
- No file output

**Pros:**
- ✅ Fastest to implement (30 min)
- ✅ Good for quick checks

**Cons:**
- ❌ Not persistent (output lost after run)
- ❌ Can't share easily
- ❌ No version history
- ❌ Hard to compare across runs

**Assessment:** Too minimal, fails to meet "dashboard" requirement

---

## Decision

✅ **Choose Option A: Pure Markdown Dashboard for Sprint 6**

### Rationale

1. **Simplicity:** Can be implemented in 1-2 hours on Day 6
2. **GitHub Integration:** Renders beautifully on GitHub, easy to review
3. **Version Control:** Markdown diffs show exactly what changed between runs
4. **No Dependencies:** Pure Python + stdlib (or simple Jinja2 template)
5. **Sufficient for 10 Models:** Text tables work well for small datasets
6. **Meets All Requirements:** Can display KPIs, model table, error breakdown
7. **Future Proof:** Can migrate to Option B/C later if needed

### Migration Path

- **Sprint 6:** Pure Markdown dashboard
- **Sprint 7:** Add HTML export option (Option B) if desired
- **Sprint 8+:** Build interactive dashboard (Option C) if >50 models or need charts

---

## Dashboard Structure

### Markdown File Layout

```
1. Header
   - Title: "GAMSLIB Benchmark Results"
   - Metadata: timestamp, tool version, tier
   
2. KPI Summary Table
   - 4 KPIs with values and targets
   - Status indicators (✅/❌)
   
3. Model Results Table
   - One row per model
   - Columns: Model, Parse, Convert, Solve, E2E, Notes
   - Status icons: ✅ PASS, ❌ FAIL, - (not attempted)
   
4. Error Breakdown
   - Parse errors by category (from Unknown 3.3)
   - Convert errors by type
   - Solve errors by PATH status
   
5. Detailed Failures Section
   - Per-model details for failures
   - Include error messages, line numbers, doc links
```

### Color/Icon Scheme

**Status Indicators:**
- ✅ Success (green checkmark)
- ❌ Failure (red X)
- ⚠️ Warning (yellow triangle)
- `-` Not attempted (gray dash)

**Target Status:**
- ✅ PASS (green)
- ❌ FAIL (red)

**Note:** These render as Unicode emojis in Markdown, no HTML/CSS needed

---

## Implementation

### Data Input Format (JSON)

```json
{
  "metadata": {
    "timestamp": "2025-11-12T14:30:00Z",
    "tool_version": "0.3.0",
    "tier": "Tier 1",
    "total_models": 10
  },
  "kpis": {
    "parse_rate": 60.0,
    "convert_rate": 83.3,
    "solve_rate": 60.0,
    "e2e_rate": 30.0,
    "meets_conservative": true,
    "meets_stretch": false
  },
  "results": [
    {
      "model_name": "trig",
      "gms_file": "trig.gms",
      "parse_status": "SUCCESS",
      "convert_status": "SUCCESS",
      "solve_status": "SUCCESS",
      "solve_time": 0.12,
      "objective_value": -3.76250149
    },
    {
      "model_name": "himmel16",
      "gms_file": "himmel16.gms",
      "parse_status": "FAILED",
      "parse_error": "Lead operator i++1 not supported",
      "parse_error_category": "INDEXED_OPERATION",
      "parse_error_line": 32,
      "convert_status": "NOT_ATTEMPTED",
      "solve_status": "NOT_ATTEMPTED"
    }
  ]
}
```

### Python Implementation

```python
# scripts/generate_gamslib_dashboard.py

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def generate_dashboard(results_json_path: Path, output_md_path: Path):
    """
    Generate Markdown dashboard from benchmark results JSON.
    
    Args:
        results_json_path: Path to benchmark results JSON file
        output_md_path: Path to output Markdown file
    """
    
    # Load results
    with open(results_json_path) as f:
        data = json.load(f)
    
    metadata = data["metadata"]
    kpis = data["kpis"]
    results = data["results"]
    
    # Generate Markdown sections
    md_parts = []
    
    # 1. Header
    md_parts.append(generate_header(metadata))
    
    # 2. KPI Summary
    md_parts.append(generate_kpi_summary(kpis, metadata["total_models"]))
    
    # 3. Model Results Table
    md_parts.append(generate_model_table(results))
    
    # 4. Error Breakdown
    md_parts.append(generate_error_breakdown(results))
    
    # 5. Detailed Failures
    md_parts.append(generate_failure_details(results))
    
    # Write to file
    markdown_content = "\n\n".join(md_parts)
    with open(output_md_path, "w") as f:
        f.write(markdown_content)
    
    print(f"Dashboard generated: {output_md_path}")

def generate_header(metadata: Dict[str, Any]) -> str:
    """Generate header section"""
    timestamp = datetime.fromisoformat(metadata["timestamp"].replace("Z", "+00:00"))
    
    return f"""# GAMSLIB Benchmark Results

**Generated:** {timestamp.strftime("%Y-%m-%d %H:%M:%S")}  
**Tool Version:** nlp2mcp {metadata["tool_version"]}  
**Model Tier:** {metadata["tier"]} ({metadata["total_models"]} models)

---"""

def generate_kpi_summary(kpis: Dict[str, Any], total: int) -> str:
    """Generate KPI summary table"""
    
    def format_kpi_row(name: str, value: float, numerator: int, denominator: int, 
                       conservative: float, stretch: float) -> str:
        cons_status = "✅ PASS" if value >= conservative else "❌ FAIL"
        stretch_status = "✅ PASS" if value >= stretch else "❌ FAIL"
        return (f"| {name} | {value:.1f}% ({numerator}/{denominator}) | "
                f"≥ {conservative:.0f}% | ≥ {stretch:.0f}% | "
                f"{cons_status} | {stretch_status} |")
    
    # Calculate counts from rates (reverse engineering)
    parse_count = int(kpis["parse_rate"] * total / 100)
    convert_count = int(kpis["convert_rate"] * parse_count / 100)
    solve_count = int(kpis["solve_rate"] * convert_count / 100)
    
    return f"""## KPI Summary

| KPI | Value | Conservative Target | Stretch Target | Status (C) | Status (S) |
|-----|-------|---------------------|----------------|------------|------------|
{format_kpi_row("Parse Rate", kpis["parse_rate"], parse_count, total, 50, 70)}
{format_kpi_row("Convert Rate", kpis["convert_rate"], convert_count, parse_count, 80, 90)}
{format_kpi_row("Solve Rate", kpis["solve_rate"], solve_count, convert_count, 50, 70)}
{format_kpi_row("E2E Success", kpis["e2e_rate"], solve_count, total, 20, 45)}

**Overall:** {"✅" if kpis["meets_conservative"] else "❌"} Conservative targets {"met" if kpis["meets_conservative"] else "not met"} | {"✅" if kpis["meets_stretch"] else "❌"} Stretch targets {"met" if kpis["meets_stretch"] else "not met"}

---"""

def generate_model_table(results: List[Dict[str, Any]]) -> str:
    """Generate model results table"""
    
    def status_icon(status: str) -> str:
        return {"SUCCESS": "✅", "FAILED": "❌", "NOT_ATTEMPTED": "-"}[status]
    
    def e2e_icon(result: Dict[str, Any]) -> str:
        if (result["parse_status"] == "SUCCESS" and 
            result["convert_status"] == "SUCCESS" and 
            result["solve_status"] == "SUCCESS"):
            return "✅"
        return "❌"
    
    def notes(result: Dict[str, Any]) -> str:
        if result["solve_status"] == "SUCCESS":
            return f"Solved in {result.get('solve_time', 0):.2f}s"
        elif result["parse_status"] == "FAILED":
            return f"Parse: {result.get('parse_error_category', 'Unknown')}"
        elif result["convert_status"] == "FAILED":
            return "Convert error"
        elif result["solve_status"] == "FAILED":
            return "PATH failed"
        return ""
    
    rows = []
    for r in results:
        rows.append(
            f"| {r['model_name']} | "
            f"{status_icon(r['parse_status'])} | "
            f"{status_icon(r['convert_status'])} | "
            f"{status_icon(r['solve_status'])} | "
            f"{e2e_icon(r)} | "
            f"{notes(r)} |"
        )
    
    return f"""## Model Results

| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
""" + "\n".join(rows) + "\n\n---"

def generate_error_breakdown(results: List[Dict[str, Any]]) -> str:
    """Generate error breakdown section"""
    
    # Count parse errors by category
    parse_errors = {}
    for r in results:
        if r["parse_status"] == "FAILED":
            category = r.get("parse_error_category", "OTHER")
            parse_errors.setdefault(category, []).append(r["model_name"])
    
    # Count convert errors
    convert_errors = sum(1 for r in results if r["convert_status"] == "FAILED")
    
    # Count solve errors
    solve_errors = sum(1 for r in results if r["solve_status"] == "FAILED")
    
    sections = ["## Error Breakdown"]
    
    # Parse errors
    if parse_errors:
        sections.append("### Parse Errors")
        sections.append("| Category | Count | Models |")
        sections.append("|----------|-------|--------|")
        for category, models in sorted(parse_errors.items()):
            sections.append(f"| {category} | {len(models)} | {', '.join(models)} |")
    
    # Convert errors
    if convert_errors > 0:
        sections.append("\n### Convert Errors")
        sections.append(f"**Total:** {convert_errors} model(s)")
    
    # Solve errors
    if solve_errors > 0:
        sections.append("\n### Solve Errors")
        sections.append(f"**Total:** {solve_errors} model(s)")
    
    return "\n".join(sections) + "\n\n---"

def generate_failure_details(results: List[Dict[str, Any]]) -> str:
    """Generate detailed failure information"""
    
    failures = [r for r in results if r.get("parse_status") == "FAILED" or 
                                     r.get("convert_status") == "FAILED" or
                                     r.get("solve_status") == "FAILED"]
    
    if not failures:
        return "## Failures\n\n*No failures!* 🎉"
    
    sections = ["## Failure Details"]
    
    for r in failures:
        sections.append(f"\n### {r['model_name']}.gms")
        
        if r["parse_status"] == "FAILED":
            sections.append(f"**Stage:** Parse")
            sections.append(f"**Category:** {r.get('parse_error_category', 'Unknown')}")
            sections.append(f"**Error:** {r.get('parse_error', 'Unknown error')}")
            if "parse_error_line" in r:
                sections.append(f"**Line:** {r['parse_error_line']}")
            sections.append(f"**Docs:** https://docs.nlp2mcp.dev/errors/#{r.get('parse_error_category', '').lower()}")
        
        elif r["convert_status"] == "FAILED":
            sections.append(f"**Stage:** Convert")
            sections.append(f"**Error:** {r.get('convert_error', 'Unknown error')}")
        
        elif r["solve_status"] == "FAILED":
            sections.append(f"**Stage:** Solve")
            sections.append(f"**Error:** {r.get('solve_error', 'Unknown error')}")
    
    return "\n".join(sections)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python generate_gamslib_dashboard.py <results.json> <output.md>")
        sys.exit(1)
    
    results_json = Path(sys.argv[1])
    output_md = Path(sys.argv[2])
    
    generate_dashboard(results_json, output_md)
```

### Usage

```bash
# Generate dashboard from benchmark results
python scripts/generate_gamslib_dashboard.py \
    results/gamslib_tier1_results.json \
    docs/benchmarks/GAMSLIB_TIER1_RESULTS.md
```

---

## Mock Dashboard

### Example Output for Sprint 6

Here's what the dashboard might look like with realistic results:

```markdown
# GAMSLIB Benchmark Results

**Generated:** 2025-11-12 14:30:00  
**Tool Version:** nlp2mcp 0.3.0  
**Model Tier:** Tier 1 (10 models)

---

## KPI Summary

| KPI | Value | Conservative Target | Stretch Target | Status (C) | Status (S) |
|-----|-------|---------------------|----------------|------------|------------|
| Parse Rate | 60.0% (6/10) | ≥ 50% | ≥ 70% | ✅ PASS | ❌ FAIL |
| Convert Rate | 83.3% (5/6) | ≥ 80% | ≥ 90% | ✅ PASS | ❌ FAIL |
| Solve Rate | 60.0% (3/5) | ≥ 50% | ≥ 70% | ✅ PASS | ❌ FAIL |
| E2E Success | 30.0% (3/10) | ≥ 20% | ≥ 45% | ✅ PASS | ❌ FAIL |

**Overall:** ✅ Conservative targets met | ❌ Stretch targets not met

---

## Model Results

| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| trig | ✅ | ✅ | ✅ | ✅ | Solved in 0.12s |
| rbrock | ✅ | ✅ | ✅ | ✅ | Solved in 0.08s |
| mhw4d | ✅ | ✅ | ✅ | ✅ | Solved in 0.15s |
| hs62 | ✅ | ✅ | ❌ | ❌ | PATH failed |
| mathopt1 | ✅ | ✅ | ❌ | ❌ | PATH failed |
| himmel16 | ❌ | - | - | ❌ | Parse: INDEXED_OPERATION |
| circle | ❌ | - | - | ❌ | Parse: DOLLAR_CONDITION |
| maxmin | ❌ | - | - | ❌ | Parse: INDEXED_OPERATION |
| mhw4dx | ❌ | - | - | ❌ | Parse: SYNTAX_ERROR |
| mingamma | ✅ | ❌ | - | ❌ | Convert error |

---

## Error Breakdown

### Parse Errors

| Category | Count | Models |
|----------|-------|--------|
| INDEXED_OPERATION | 2 | himmel16, maxmin |
| DOLLAR_CONDITION | 1 | circle |
| SYNTAX_ERROR | 1 | mhw4dx |

### Convert Errors

**Total:** 1 model(s)

### Solve Errors

**Total:** 2 model(s)

---

## Failure Details

### himmel16.gms

**Stage:** Parse  
**Category:** INDEXED_OPERATION  
**Error:** Lead operator i++1 not supported  
**Line:** 32  
**Docs:** https://docs.nlp2mcp.dev/errors/#indexed-operation

### circle.gms

**Stage:** Parse  
**Category:** DOLLAR_CONDITION  
**Error:** Dollar condition $(ord(i) < ord(j)) not supported  
**Line:** 18  
**Docs:** https://docs.nlp2mcp.dev/errors/#dollar-condition

[... more failures ...]
```

---

## Implementation Plan for Day 6

When Unknown 3.4 resolution is applied:

### Step 1: Create Dashboard Generator Script (1h)

Create `scripts/generate_gamslib_dashboard.py` with:
- JSON input parser
- Markdown section generators (header, KPIs, table, errors)
- File writer
- Command-line interface

### Step 2: Integrate with Benchmark Script (30min)

Modify `scripts/gamslib_benchmark.py` to:
- Save results to JSON after execution
- Automatically invoke dashboard generator
- Place output in `docs/benchmarks/GAMSLIB_TIER1_RESULTS.md`

### Step 3: Test Dashboard Generation (30min)

Test with:
- Empty results (0 models)
- All pass scenario (100% success)
- All fail scenario (0% success)
- Realistic scenario (mixed results)

### Step 4: Documentation (30min)

Update README to:
- Explain how to run benchmark
- Show example dashboard output
- Link to generated dashboard

### Estimated Implementation Time: 2.5 hours on Day 6

---

## Test Cases

### Test 1: Empty Results
```python
data = {
    "metadata": {"total_models": 0, ...},
    "kpis": {"parse_rate": 0, "convert_rate": 0, "solve_rate": 0, "e2e_rate": 0},
    "results": []
}
generate_dashboard(data, output_path)
# Should generate valid dashboard with "No models tested"
```

### Test 2: All Pass
```python
data = {
    "metadata": {"total_models": 2, ...},
    "kpis": {"parse_rate": 100, "convert_rate": 100, "solve_rate": 100, "e2e_rate": 100},
    "results": [
        {"model_name": "m1", "parse_status": "SUCCESS", "convert_status": "SUCCESS", "solve_status": "SUCCESS"},
        {"model_name": "m2", "parse_status": "SUCCESS", "convert_status": "SUCCESS", "solve_status": "SUCCESS"}
    ]
}
generate_dashboard(data, output_path)
# Should show all ✅ and 100% KPIs
```

### Test 3: Realistic Mixed Results
Use the example data from Unknown 3.5 test case 4 (6 parse, 5 convert, 3 solve).

---

## Deliverable

This research document confirms:

✅ **Pure Markdown dashboard chosen for Sprint 6**  
✅ **Dashboard structure defined (header, KPIs, table, errors, details)**  
✅ **JSON input format specified**  
✅ **Python implementation provided with full code**  
✅ **Mock dashboard example created**  
✅ **Icon/color scheme defined using Unicode emojis**  
✅ **Implementation plan defined for Day 6**  
✅ **Test cases defined for validation**

**Ready for Day 6 implementation:** Yes

---

## References

- Unknown 3.3: Parse Error Categories (`docs/research/gamslib_parse_errors_preliminary.md`)
- Unknown 3.5: KPI Definitions (`docs/research/gamslib_kpi_definitions.md`)
- Unknown 4.2: Documentation Links (`docs/research/doc_link_strategy.md`)
- Task 8: GAMSLIB Benchmark Script (`scripts/gamslib_benchmark.py`)
- Task 9: Dashboard Generator (`scripts/generate_gamslib_dashboard.py`)
- KNOWN_UNKNOWNS.md: Unknown 3.4 (lines 884-958)
